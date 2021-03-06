# %%
# Standard library
from dataclasses import dataclass, field
from typing import ClassVar, List, Set, Dict, Tuple, Optional

# External packages
import pandas as pd
from tqdm import tqdm

# Local packages
from evaluation_jp.data import ModelDataHandler
from evaluation_jp.models import PopulationSliceGenerator, TreatmentPeriodGenerator

# //TODO Read EvaluationModel parameters from yml file
@dataclass
class EvaluationModel:

    # Init parameters
    data_handler: ModelDataHandler = None
    population_slice_generator: PopulationSliceGenerator = None
    treatment_period_generator: TreatmentPeriodGenerator = None
    # outcome_generator: OutcomeGenerator = None

    # Attributes - set up post init
    data: pd.DataFrame = None
    population_slices: dict = None
    treatment_periods: dict = None

    def add_population_slices(self):
        self.population_slices = {}
        with tqdm(
            total=len(self.population_slice_generator.date_range), position=0
        ) as t:
            for i, population_slice in enumerate(
                self.population_slice_generator.run(self.data_handler)
            ):
                t.set_description(f"Slice {i+1}")
                self.population_slices[population_slice.id] = population_slice
                t.set_postfix(
                    slice=population_slice.id.date.date(),
                    pop=len(population_slice.data),
                )
                t.update()

    @property
    def total_population(self):
        return set().union(*(s.data.index for s in self.population_slices.values()))

    @property
    def total_eligible_population(self):
        return set().union(
            *(
                s.data[s.data["eligible_population"]].index
                for s in self.population_slices.values()
            )
        )

    # Get each data source and add to master dataframe
    # Save dataframe using MDH

    def add_treatment_periods(self):
        self.treatment_periods = {}
        with tqdm(
            total=len(self.population_slice_generator.date_range), position=0
        ) as t0:
            for i, population_slice in enumerate(self.population_slices.values()):
                t0.set_description(f"Periods for slice {i+1}")
                with tqdm(
                    total=len(
                        self.treatment_period_generator.treatment_period_range(
                            population_slice.id.date
                        )
                    ),
                    position=1,
                ) as t1:
                    for j, t_period in enumerate(
                        self.treatment_period_generator.run(
                            population_slice, self.data_handler
                        )
                    ):
                        t1.set_description(f"Period {j+1}")
                        self.treatment_periods[t_period.id] = t_period
                        t1.set_postfix(
                            period=t_period.id.time_period, pop=len(t_period.data)
                        )
                        t1.update()
                t0.set_postfix(
                    slice=population_slice.id.date.date(),
                    pop=len(population_slice.data),
                )
                t0.update()

    # //TODO Run weighting algorithm for periods

    # //TODO Back-propagations of weights through periods

    # //TODO Add outcomes with weighting
