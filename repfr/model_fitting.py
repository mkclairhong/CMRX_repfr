# AUTOGENERATED! DO NOT EDIT! File to edit: 06_Fitting_By_MSE.ipynb (unless otherwise specified).

__all__ = ['cmr_rep_likelihood', 'cmr_rep_objective_function', 'cmr_rep_mse', 'cmr_rep_mse_objective_function']

# Cell

import numpy as np
from numba import njit
from .models import DefaultCMR

@njit(fastmath=True, nogil=True)
def cmr_rep_likelihood(
        trials, presentations, list_types, list_length, encoding_drift_rate, start_drift_rate,
        recall_drift_rate, shared_support, item_support, learning_rate,
        primacy_scale, primacy_decay, stop_probability_scale,
        stop_probability_growth, choice_sensitivity):
    """
    Generalized cost function for fitting the InstanceCMR model optimized
    using the numba library.

    Output scales inversely with the likelihood that the model and specified
    parameters would generate the specified trials. For model fitting, is
    usually wrapped in another function that fixes and frees parameters for
    optimization.

    **Arguments**:
    - data_to_fit: typed list of int64-arrays where rows identify a unique
        trial of responses and columns corresponds to a unique recall index.
    - A configuration for each parameter of `InstanceCMR` as delineated in
        `Formal Specification`.

    **Returns** the negative sum of log-likelihoods across specified trials
    conditional on the specified parameters and the mechanisms of InstanceCMR.
    """

    likelihood = np.ones((len(trials), list_length))

    # we can use the same model for list types 1 and 2
    stable_models = [DefaultCMR(
            list_length, list_length, encoding_drift_rate, start_drift_rate,
            recall_drift_rate, shared_support, item_support, learning_rate,
            primacy_scale, primacy_decay, stop_probability_scale,
            stop_probability_growth, choice_sensitivity),
                    DefaultCMR(
            int(list_length/2), list_length, encoding_drift_rate, start_drift_rate,
            recall_drift_rate, shared_support, item_support, learning_rate,
            primacy_scale, primacy_decay, stop_probability_scale,
            stop_probability_growth, choice_sensitivity)]
    stable_models[0].experience(np.eye(list_length, list_length))
    stable_models[1].experience(np.eye(int(list_length/2), int(list_length/2))[np.repeat(np.arange(int(list_length/2)), 2)])

    for trial_index in range(len(trials)):

        item_count = np.max(presentations[trial_index])+1

        if list_types[trial_index] > 2:
            model = DefaultCMR(
                item_count, list_length, encoding_drift_rate, start_drift_rate,
                recall_drift_rate, shared_support, item_support, learning_rate,
                primacy_scale, primacy_decay, stop_probability_scale,
                stop_probability_growth, choice_sensitivity)

            model.experience(np.eye(item_count, item_count)[presentations[trial_index]])
        else:
            model = stable_models[list_types[trial_index]-1]

        trial = trials[trial_index]

        model.force_recall()
        for recall_index in range(len(trial) + 1):

            # identify index of item recalled; if zero then recall is over
            if recall_index == len(trial) and len(trial) < item_count:
                recall = 0
            elif trial[recall_index] == 0:
                recall = 0
            else:
                recall = presentations[trial_index][trial[recall_index]-1] + 1

            # store probability of and simulate recalling item with this index
            likelihood[trial_index, recall_index] = \
                model.outcome_probabilities(model.context)[recall]

            if recall == 0:
                break
            model.force_recall(recall)

        # reset model to its pre-retrieval (but post-encoding) state
        model.force_recall(0)

    return -np.sum(np.log(likelihood))

# Cell

def cmr_rep_objective_function(data_to_fit, presentations, list_types, list_length, fixed_parameters, free_parameters):
    """
    Generates and returns an objective function for input to support search
    through parameter space for ICMR model fit using an optimization function.

    Arguments:
    - fixed_parameters: dictionary mapping parameter names to values they'll
        be fixed to during search, overloaded by free_parameters if overlap
    - free_parameters: list of strings naming parameters for fit during search
    - data_to_fit: array where rows identify a unique trial of responses and
        columns corresponds to a unique recall index

    Returns a function that accepts a vector x specifying arbitrary values for
    free parameters and returns evaluation of icmr_likelihood using the model
    class, all parameters, and provided data.
    """
    return lambda x: cmr_rep_likelihood(data_to_fit, presentations, list_types, list_length, **{**fixed_parameters, **{
        free_parameters[i]:x[i] for i in range(len(x))}})

# Cell
from numba import njit
from .model_analysis import recall_probability_by_lag
from .models import DefaultCMR as CMR
import numpy as np

@njit(fastmath=True, nogil=True)
def cmr_rep_mse(
    curve, presentations, list_types, experiment_count, presentation_count,
    encoding_drift_rate, start_drift_rate, recall_drift_rate,
    shared_support, item_support, learning_rate, primacy_scale, primacy_decay,
    stop_probability_scale, stop_probability_growth, choice_sensitivity):
    """
    Apply organizational analyses to visually compare the behavior of the model
    with these parameters against specified dataset.
    """

    # we can use the same model for list types 1 and 2
    stable_models = [
        CMR(
            presentation_count, presentation_count, encoding_drift_rate, start_drift_rate,
            recall_drift_rate, shared_support, item_support, learning_rate,
            primacy_scale, primacy_decay, stop_probability_scale,
            stop_probability_growth, choice_sensitivity),
        CMR(
            int(presentation_count/2), presentation_count, encoding_drift_rate, start_drift_rate,
            recall_drift_rate, shared_support, item_support, learning_rate,
            primacy_scale, primacy_decay, stop_probability_scale,
            stop_probability_growth, choice_sensitivity)]
    stable_models[0].experience(np.eye(list_length, list_length))
    stable_models[1].experience(np.eye(int(list_length/2), int(list_length/2))[np.repeat(np.arange(int(list_length/2)), 2)])

    total_presented, total_retrieved = np.zeros(5), np.zeros(5)

    # generate simulation data from model
    sim = np.zeros((np.shape(presentations)[0] * experiment_count,
                   np.shape(presentations)[1]))
    sim = sim.astype(np.int_)
    for trial_index, presentation in enumerate(presentations):

        item_count = np.max(presentation)+1

        if list_types[trial_index] > 2:
            model = CMR(
                item_count, presentation_count, encoding_drift_rate, start_drift_rate,
                recall_drift_rate, shared_support, item_support, learning_rate,
                primacy_scale, primacy_decay, stop_probability_scale,
                stop_probability_growth, choice_sensitivity)

            model.experience(np.eye(item_count, item_count)[presentations[trial_index]])
        else:
            model = stable_models[list_types[trial_index]-1]

        # free recall for specified number of experiments
        for experiment in range(experiment_count):
            recalled = model.free_recall() + 1
            sim[trial_index * experiment_count + experiment, :len(recalled)] = recalled

    return np.mean(np.square(recall_probability_by_lag(presentations, sim, experiment_count)[-1] - curve))

# Cell

def cmr_rep_mse_objective_function(data_to_fit, presentations, list_types, experiment_count,
                                   list_length, fixed_parameters, free_parameters):
    """
    Generates and returns an objective function for input to support search
    through parameter space for ICMR model fit using an optimization function.

    Arguments:
    - fixed_parameters: dictionary mapping parameter names to values they'll
        be fixed to during search, overloaded by free_parameters if overlap
    - free_parameters: list of strings naming parameters for fit during search
    - data_to_fit: array where rows identify a unique trial of responses and
        columns corresponds to a unique recall index

    Returns a function that accepts a vector x specifying arbitrary values for
    free parameters and returns evaluation of icmr_likelihood using the model
    class, all parameters, and provided data.
    """
    return lambda x: cmr_rep_mse(data_to_fit, presentations, list_types, experiment_count, list_length, **{**fixed_parameters, **{
        free_parameters[i]:x[i] for i in range(len(x))}})