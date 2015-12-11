from functools import partial
from menpo.feature import no_op
from menpofit.math.regression import OPPRegression
from menpofit.result import euclidean_bb_normalised_error

from .base import (BaseSupervisedDescentAlgorithm,
                   compute_parametric_delta_x, features_per_image,
                   features_per_patch, update_parametric_estimates,
                   print_parametric_info, fit_parametric_shape)
from menpofit.math import (IIRLRegression, IRLRegression,
                           OptimalLinearRegression, PCRRegression)


# TODO: document me!
from menpofit.modelinstance import OrthoPDM


class ParametricShapeSDAlgorithm(BaseSupervisedDescentAlgorithm):
    r"""
    """

    def __init__(self, shape_model_cls=OrthoPDM):
        super(ParametricShapeSDAlgorithm, self).__init__()
        self.regressors = []
        self.shape_model_cls = shape_model_cls
        self.shape_model = None

    def _compute_delta_x(self, gt_shapes, current_shapes):
        # This is called first - so train shape model here
        if self.shape_model is None:
            self.shape_model = self.shape_model_cls(gt_shapes)

        return compute_parametric_delta_x(gt_shapes, current_shapes,
                                          self.shape_model)

    def _update_estimates(self, estimated_delta_x, delta_x, gt_x,
                          current_shapes):
        update_parametric_estimates(estimated_delta_x, delta_x, gt_x,
                                    current_shapes, self.shape_model)

    def _compute_training_features(self, images, gt_shapes, current_shapes,
                                   prefix='', verbose=False):
        # initialize sample counter
        return features_per_image(images, current_shapes, self.patch_shape,
                                  self.patch_features, prefix=prefix,
                                  verbose=verbose)

    def _compute_test_features(self, image, current_shape):
        return features_per_patch(image, current_shape,
                                  self.patch_shape, self.patch_features)

    def run(self, image, initial_shape, gt_shape=None, **kwargs):
        return fit_parametric_shape(image, initial_shape, self,
                                    gt_shape=gt_shape)

    def _print_regression_info(self, _, gt_shapes, n_perturbations,
                               delta_x, estimated_delta_x, level_index,
                               prefix=''):
        print_parametric_info(self.shape_model, gt_shapes, n_perturbations,
                              delta_x, estimated_delta_x, level_index,
                              self._compute_error, prefix=prefix)


class ParametricShapeNewton(ParametricShapeSDAlgorithm):
    r"""
    """

    def __init__(self, patch_features=no_op, patch_shape=(17, 17),
                 n_iterations=3, shape_model_cls=OrthoPDM,
                 compute_error=euclidean_bb_normalised_error,
                 eps=10 ** -5, alpha=0, bias=True):
        super(ParametricShapeNewton, self).__init__(
            shape_model_cls=shape_model_cls)

        self._regressor_cls = partial(IRLRegression, alpha=alpha, bias=bias)
        self.patch_shape = patch_shape
        self.patch_features = patch_features
        self.n_iterations = n_iterations
        self._compute_error = compute_error
        self.eps = eps


# TODO: document me!
class ParametricShapeGaussNewton(ParametricShapeSDAlgorithm):
    r"""
    """

    def __init__(self, patch_features=no_op, patch_shape=(17, 17),
                 n_iterations=3, shape_model_cls=OrthoPDM,
                 compute_error=euclidean_bb_normalised_error,
                 eps=10 ** -5, alpha=0, bias=True, alpha2=0):
        super(ParametricShapeGaussNewton, self).__init__(
            shape_model_cls=shape_model_cls)

        self._regressor_cls = partial(IIRLRegression, alpha=alpha, bias=bias,
                                      alpha2=alpha2)
        self.patch_shape = patch_shape
        self.patch_features = patch_features
        self.n_iterations = n_iterations
        self._compute_error = compute_error
        self.eps = eps


class ParametricShapeOptimalRegression(ParametricShapeSDAlgorithm):
    r"""
    """

    def __init__(self, patch_features=no_op, patch_shape=(17, 17),
                 n_iterations=3, shape_model_cls=OrthoPDM,
                 compute_error=euclidean_bb_normalised_error,
                 eps=10 ** -5, variance=None, bias=True):
        super(ParametricShapeOptimalRegression, self).__init__(
            shape_model_cls=shape_model_cls)

        self._regressor_cls = partial(OptimalLinearRegression,
                                      variance=variance, bias=bias)
        self.patch_shape = patch_shape
        self.patch_features = patch_features
        self.n_iterations = n_iterations
        self._compute_error = compute_error
        self.eps = eps


class ParametricShapePCRRegression(ParametricShapeSDAlgorithm):
    r"""
    """

    def __init__(self, patch_features=no_op, patch_shape=(17, 17),
                 n_iterations=3, shape_model_cls=OrthoPDM,
                 compute_error=euclidean_bb_normalised_error,
                 eps=10 ** -5, variance=None, bias=True):
        super(ParametricShapePCRRegression, self).__init__(
            shape_model_cls=shape_model_cls)

        self._regressor_cls = partial(PCRRegression,
                                      variance=variance, bias=bias)
        self.patch_shape = patch_shape
        self.patch_features = patch_features
        self.n_iterations = n_iterations
        self._compute_error = compute_error
        self.eps = eps


class ParametricShapeOPPRegression(ParametricShapeSDAlgorithm):
    r"""
    """

    def __init__(self, patch_features=no_op, patch_shape=(17, 17),
                 n_iterations=3, shape_model_cls=OrthoPDM,
                 compute_error=euclidean_bb_normalised_error,
                 eps=10 ** -5, whiten=False, bias=True):
        super(ParametricShapeOPPRegression, self).__init__(
            shape_model_cls=shape_model_cls)

        self._regressor_cls = partial(OPPRegression,
                                      whiten=whiten, bias=bias)
        self.patch_shape = patch_shape
        self.patch_features = patch_features
        self.n_iterations = n_iterations
        self._compute_error = compute_error
        self.eps = eps