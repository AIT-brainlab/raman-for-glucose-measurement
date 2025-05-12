import numpy as np
from sklearn.linear_model import LinearRegression  # type: ignore

# from sklearn.linear_model._base import LinearModel
# from sklearn.base import MultiOutputMixin, RegressorMixin


class EMSC:

    raman_shift: np.ndarray
    baseline: np.ndarray
    order: int

    reference: np.ndarray = None  # type: ignore
    # noise:np.ndarray = None
    ref_names: list[str] = []

    model: LinearRegression = LinearRegression(fit_intercept=False)
    _loss: float = None  # type: ignore
    # _noise:np.ndarray = None

    def __init__(self, raman_shift: np.ndarray, order: int = 5):
        assert len(raman_shift.shape) == 1
        self.raman_shift = raman_shift
        self.order = order
        # baseline has a shape of (raman_shift, order + 1)
        self.baseline = np.vstack(
            [np.power(self.raman_shift, o) for o in range(self.order + 1)]
        ).T
        assert self.baseline.shape == (self.raman_shift.shape[0], self.order + 1)

    @property
    def x_range(self) -> tuple:
        return self.raman_shift.shape

    @property
    def X(self) -> np.ndarray:
        return np.hstack((self.reference, self.baseline))

    @property
    def coefficients(self) -> np.ndarray:
        return self.model.coef_

    @property
    def loss(self) -> float:
        if self._loss is None:
            raise RuntimeError(f"The model has not been fitted yet.")
        return self._loss

    def add_reference(self, reference: np.ndarray, name: str = ""):
        assert len(reference.shape) == 1
        assert reference.shape == self.x_range

        # shape of reference is (raman_shift, 1)
        reference = reference.reshape(-1, 1)
        if isinstance(self.reference, type(None)):
            self.reference = reference
        else:
            self.reference = np.hstack((self.reference, reference))
        self.ref_names.append(name)

    def fit(self, composite_signal: np.ndarray):
        assert len(composite_signal.shape) == 1
        assert composite_signal.shape == self.x_range
        self.model.fit(X=self.X, y=composite_signal)

        # shape of _predicted is (raman_shift, 1)
        self._predicted = self.model.predict(X=self.X)
        assert len(self._predicted.shape) == 1
        assert self._predicted.shape == self.x_range

        self._loss = self.model.score(X=self.X, y=composite_signal)
        return self.model

    def transform(
        self, composite_signal: np.ndarray, normalize: bool = True
    ) -> np.ndarray:
        # Background is everything but the first reference
        background = np.dot(self.X[:, 1:], self.coefficients[1:])
        self._corrected = (composite_signal - background) / self.coefficients[0]

        if normalize:
            self._corrected = (self._corrected - self._corrected.min()) / (
                self._corrected.max() - self._corrected.min()
            )

        return self._corrected
