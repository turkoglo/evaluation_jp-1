# %%
## Standard library


## External packages
import pandas as pd

## Local packages
from evaluation_jp.models import (
    EvaluationModel,
    PopulationSliceGenerator,
    TreatmentPeriodGenerator,
)
from evaluation_jp.features import SetupSteps
from evaluation_jp.data import ModelDataHandler


em = EvaluationModel(
    data_handler=ModelDataHandler(
        database_type="sqlite",
        location="//cskma0294/f/Evaluations/JobPath",
        name="test",
    ),
    population_slice_generator=PopulationSliceGenerator(
        start=pd.Timestamp("2016-01-01"),
        end=pd.Timestamp("2017-12-31"),
        freq="QS",
        setup_steps_by_date={
            pd.Timestamp("2016-01-01"): SetupSteps(
                steps=[
                    # LiveRegisterPopulation(cols=[SPECIFY]),
                    # AgeEligible(max_eligible=(60, "years")),
                    # ClaimCodeEligible(eligible_codes=["UA", "UB"]),
                    # ClaimDurationEligible(min_eligible=(1, "years")),
                    # OnLES(assumed_episode_length=(1, "years")),
                    # OnJobPath(
                    #     assumed_episode_length=(1, "years"), data_source="jobpath",
                    # ),
                    # EvaluationEligible(
                    #     eligibility_criteria={
                    #         "age_eligible": True,
                    #         "claim_code_eligible": True,
                    #         "claim_duration_eligible": True,
                    #         "on_les": False,
                    #         "on_jobpath": False,
                    #     }
                    # ),
                ]
            )
        },
    ),
    treatment_period_generator=TreatmentPeriodGenerator(
        end=pd.Period("2017-12"),
        freq="M",
        setup_steps_by_date={
            pd.Timestamp("2016-01-01"): SetupSteps(
                steps=[
                    # on_lr={"period_type": period_freq, "when": "end"},
                    # code={"eligible_codes": ("UA", "UB")},
                    # duration={"min_duration": pd.DateOffset(years=1)},
                    # # not_on_les={"episode_duration": pd.DateOffset(years=1)},
                    # not_on_jobpath={
                    #     "episode_duration": pd.DateOffset(years=1),
                    #     "use_jobpath_data": True,
                    #     "use_ists_data": False,
                    #     "combine": "either",
                    # },
                    # not_jobpath_hold={"period_type": period_freq, "how": "end"},
                    # not_les_starts={"period_type": period_freq}
                ]
            )
        },
    ),
    # outcome_generator = OutcomeGenerator(
    # outcome_start_date=pd.Timestamp("2016-02-01"),
    # outcome_end_date=pd.Timestamp("2019-02-01"),
    # )
)
