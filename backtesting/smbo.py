from pprint import pprint
from typing import Callable, TYPE_CHECKING, Union

from scipy.optimize import NonlinearConstraint, OptimizeResult
from scipy.spatial.distance import cdist
from scipy.stats import qmc
from sklearn.base import BaseEstimator
from sklearn.decomposition import KernelPCA
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.kernel_approximation import Nystroem
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR

try:
    from joblib import hash as joblib_hash, Parallel, delayed
except ImportError:
    if not TYPE_CHECKING:
        joblib_hash = hash
        Parallel = lambda *a, **kw: list
        delayed = lambda f: f
import numpy as np
from sklearn.ensemble import (
    ExtraTreesRegressor, GradientBoostingRegressor,
)
from sklearn.preprocessing import LabelEncoder, StandardScaler


def array_set_difference(A, B):
    """Remove from A all rows present in B, i.e. A - B (or A \ B)."""
    dtype = np.dtype((np.void, A.dtype.itemsize * A.shape[1]))  # 1d byte strings for row-wise comparison
    A_structured = np.ascontiguousarray(A).view(dtype)
    B_structured = np.ascontiguousarray(B).view(dtype)
    mask = ~np.in1d(A_structured, B_structured)
    return A[mask]


class ExtraTreesRegressorWithStd(ExtraTreesRegressor):
    def predict(self, X):
        preds = np.array([tree.predict(X) for tree in self.estimators_])
        mean = preds.mean(axis=0)
        std = preds.std(axis=0)
        return mean, std


class SMBOptimizer:
    def __init__(
            self, *,
            n_estimators: int = 20,
            n_iter: int = 100,
            n_init: Union[int, float] = .1,
            n_candidates: int = 1,
            decimals: int = 8,
            alpha: float = 1e-3,
            tol: float = 1e-6,
            model: BaseEstimator = None,
            **kwargs,
    ):
        self.best_bounds = {}
        self.n_init = n_init
        self.n_iter = n_iter
        self.n_candidates = n_candidates
        self.alpha = alpha
        self.tol = tol
        self._label_encoders = {}
        self._bounds = None
        self.decimals = decimals
        if model is None:
            model = ExtraTreesRegressorWithStd(n_estimators=n_estimators, **kwargs)
        self.model = model

    def _make_random_X(self, n_samples: int | float = None, constraint = None, sampler=None):
        if sampler == 'sobol':
            sampler = qmc.Sobol(len(self._bounds), optimization='random-cd')
        elif sampler == 'lhc':
            sampler = qmc.LatinHypercube(len(self._bounds), optimization='random-cd')

        A = []
        for _ in range(10_000):
            if sampler is not None:
                X = sampler.random(n_samples)
                # X = np.array([
                #     np.interp(X[:, i], [0, 1], self.best_bounds.get(key, values))
                #     for i, (key, (dtype, values)) in enumerate(self._bounds.items())
                # ]).T
                # lb, ub = [], []
                # for i, (key, (dtype, values)) in enumerate(self._bounds.items()):
                #     values = self.best_bounds.get(key, values)
                #     lb.append(values.min() if dtype is object else values[0])
                #     ub.append(values.max() if dtype is object else values[1])
                # X = qmc.scale(sample, lb, ub)
                for i, (key, (dtype, values)) in enumerate(self._bounds.items()):
                    if dtype in (int, float):
                        X[:, i] = np.interp(X[:, i], [0, 1], self.best_bounds.get(key, values))
                        if dtype is int:
                            X[:, i] = np.round(X[:, i])
                    elif dtype is object:
                        X[:, i] = np.round(np.interp(X[:, i], [0, 1], [0, len(values) - 1])).astype(int)

            else:
                X = []
                for key, (dtype, values) in self._bounds.items():
                    values = self.best_bounds.get(key, values)
                    if dtype is float:
                        X.append(np.round(np.random.uniform(min(values), max(values), n_samples), self.decimals))
                    elif dtype is int:
                        X.append(np.random.randint(min(values), max(values) + 1, n_samples))
                    else:
                        assert dtype is object, dtype
                        X.append(np.random.randint(len(values), size=n_samples))
                X = np.column_stack(X)

            if constraint is not None:
                X = X[np.apply_along_axis(lambda x: bool(constraint(x)), 1, self._inverse_transform(X))]
            A.append(X)
            if sum(map(len, A)) >= n_samples:
                break
        else:
            raise RuntimeError('Constraint cannot be satisfied')
        A = np.row_stack(A)  #[:n_samples]
        return A

    def _suggest(self, n_candidates, constraint, exploitation_coef):
        n_points = max(5_000, 100 * len(self._bounds))
        X = self._make_random_X(n_points, constraint=constraint)
        pred = self.model.predict(X)
        try:
            mean, std = pred
        except ValueError:
            mean, std = pred, 0
        # Begin with exploring, end with exploiting
        criterion = mean + (-2 + 3 * exploitation_coef) * std
        best_indices = np.argsort(criterion)[:n_points // 10]
        best_points = []
        thresh = .1 * np.std(X, axis=0).mean()
        for idx in best_indices:
            if all(cdist([X[idx]], [X[prev]])[0, 0] > thresh
                   for prev in best_points):
                best_points.append(idx)
                if len(best_points) == n_candidates:
                    break
        return X[best_points]

    # def _inverse_transform(self, x):
    #     x = list(x)
    #     for i, (key, (_, values)) in enumerate(self._bounds.items()):
    #         encoder = self._label_encoders.get(key)
    #         if encoder:
    #             x[i] = encoder.inverse_transform([int(x[i])])[0]
    #     return x

    def _inverse_transform(self, X: np.ndarray) -> np.ndarray:
        if self._label_encoders:
            X = X.astype(object)
            for i, (key, (_, values)) in enumerate(self._bounds.items()):
                if encoder := self._label_encoders.get(key):
                    X[:, i] = encoder.inverse_transform(X[:, i].astype(int))
        return X

    def _update_bounds(self, X, y, *, alpha):
        best_points = X[np.argsort(y)[:max(1, int(len(y) * alpha))]]
        for i, (key, (dtype, _)) in enumerate(self._bounds.items()):
            # Only for non-categorical dimensions
            # TODO: Add bounds-narrowing for categoricals
            if key in self._label_encoders:
                continue
            values = best_points[:, i]
            self.best_bounds[key] = np.array([np.min(values), np.max(values)],
                                             dtype=int if dtype is int else float)

    def optimize(
            self,
            objective_func: Callable[[tuple], Union[float, tuple[float, float]]],
            constraint: Callable[[np.ndarray], bool] = None,
            **kwargs,
    ):
        self._bounds = kwargs
        for key, values in list(kwargs.items()):
            values = np.asarray(values)
            dtype = (int if np.issubdtype(values.dtype, np.int_) else
                     float if np.issubdtype(values.dtype, np.float_) else
                     object)
            self._bounds[key] = dtype, values
            if dtype is object:
                enc = self._label_encoders[key] = LabelEncoder()
                enc.fit(values)

        n_init = self.n_init
        if isinstance(n_init, float):
            n_init = int(max(n_init * self.n_iter, 2**(len(self._bounds) + 1)))

        if isinstance(constraint, NonlinearConstraint):
            constraint = constraint.fun

        X = self._make_random_X(n_init, constraint=constraint, sampler='sobol')
        parallel = Parallel(n_jobs=-1, prefer='threads', require="sharedmem")
        y = np.array(parallel(delayed(objective_func)(x) for x in self._inverse_transform(X)))
        print(X)
        print(y)

        try:
            y, sample_weight = y.T
        except ValueError:
            sample_weight = None

        from tqdm.auto import tqdm
        for n_iter in tqdm(range(1, self.n_iter + 1),
                            desc=f'{self.__class__.__name__} ({objective_func.__name__})',
                           disable=True):
            self.model.fit(X, y, sample_weight=sample_weight)
            x_new = self._suggest(n_candidates=self.n_candidates,
                                  constraint=constraint,
                                  exploitation_coef=n_iter / self.n_iter)

            x_new = array_set_difference(x_new, X)
            if not len(x_new):
                # TODO: No new points
                break

            y_new = parallel(delayed(objective_func)(x) for x in self._inverse_transform(x_new))
            if sample_weight is not None:
                y_new, w = y_new
                sample_weight = np.append(sample_weight, w)
            else:
                w = ''
            print(w, x_new, y_new)
            pprint(self.best_bounds)

            X = np.row_stack((X, x_new))
            y = np.append(y, y_new)

            cummin = np.minimum.accumulate(np.sort(y)[::-1][-3:])
            if cummin[0] - cummin[-1] <= self.tol:
                break

            self._update_bounds(X, y, alpha=(1 - self.alpha) ** n_iter)

        pprint(self.best_bounds)

        result = OptimizeResult(
            x=X[np.argmin(y)],
            fun=np.min(y),
            success=True,
            nfev=len(y),
            nit=n_iter,
            x_iters=X,
            func_vals=y
        )
        return result


# Example Usage

cnt = 0
def objective_function(x):
    # Rosenbrock function constrained with a cubic and a line
    # https://en.wikipedia.org/wiki/Test_functions_for_optimization#Test_functions_for_constrained_optimization
    global cnt
    cnt += 1
    print('x', cnt)
    return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2


def constraint(x):
    # return 1
    return x[0]**2 + x[1]**2 <= 2
    return (x[2] == 'a' and
            (x[0] - 1)**3 - x[1] + 1 <= 0 and
            x[0] + x[1] - 2 <= 0)


optimizer = SMBOptimizer(n_init=.1, n_iter=100, decimals=4, alpha=0.01, tol=1e-5, n_candidates=1)

res = optimizer.optimize(objective_function, constraint=constraint,
                         x1=(-2, 2), x2=(-.5, 2.5), obj=('a', 'b'))

print("Best parameters found:", res.x)
print("Function value:", res.fun)
