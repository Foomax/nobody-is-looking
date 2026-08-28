# R-15c: the headline's own notebook (more_layers_r2.ipynb cells 8-9, 12-13) over the regenerated r2_expt activations.
import sys, os, pickle, json
LP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src/subteams/LLMProbing'); sys.path.insert(0, LP); os.chdir(LP)
E = os.path.dirname(os.path.abspath(__file__))
from experiments import scalar_prediction_experiment
from experiments.utils import summarise_experiment
activations_path = f'{E}/data/activations/r2_expt'; probes_path = f'{E}/data/probes/threshold_r2_probes_more_layers'; os.makedirs(probes_path, exist_ok=True)
res = scalar_prediction_experiment('r2_score', activations_path, probes_path, lr=0.01, num_epochs=15, layers=list(range(4, 16)), r2_threshold=0.5, num_repeats=3)
pickle.dump(res, open(f'{probes_path}/experiment_data.pt', 'wb'))
summ = summarise_experiment(res, incl_extras=True)
print('SUMMARY_TABLE'); print(summ.to_string())
summ.to_csv(f'{E}/more_layers_r2_summary.csv', index=False)
