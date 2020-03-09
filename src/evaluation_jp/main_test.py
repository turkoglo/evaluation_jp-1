# %%
## Standard library
from typing import ClassVar, List, Set, Dict, Tuple, Optional

## External packages
import pandas as pd

## Local packages
from src.evaluation_model import EvaluationModel
from src.features.selection_helpers import EligibilityChecker, EligibilityCheckManager

slice_freq = 'Q'
period_freq = 'M'

slice_evaluation_eligibility_checker = EligibilityCheckManager(
    checks_by_startdate={
        pd.Timestamp("2016-01-01"): EligibilityChecker(
            age={"max_age": pd.DateOffset(years=60)},
            on_lr={"when": "start"},
            code={"eligible_codes": ("UA", "UB")},
            duration={"min_duration": pd.DateOffset(years=1)},
            not_on_les={"episode_duration": pd.DateOffset(years=1)},
            not_on_jobpath={
                "episode_duration": pd.DateOffset(years=1),
                "use_jobpath_data": True,
                "use_ists_data": False,
                "combine": "either",
            },
        ),
    }
)
period_eligibility_checker = EligibilityCheckManager(
    checks_by_startdate={
        pd.Timestamp("2016-01-01"): EligibilityChecker(
            on_lr={"period_type": period_freq, "when": "end"},
            code={"eligible_codes": ("UA", "UB")},
            duration={"min_duration": pd.DateOffset(years=1)},
            # not_on_les={"episode_duration": pd.DateOffset(years=1)},
            not_on_jobpath={
                "episode_duration": pd.DateOffset(years=1),
                "use_jobpath_data": True,
                "use_ists_data": False,
                "combine": "either",
            },
            not_jobpath_hold={"period_type": period_freq, "how": "end"},
            # not_les_starts={"period_type": period_freq}
        ),
    }
)

em = EvaluationModel(
    ## Model
    start_date=pd.Timestamp("2016-01-01"),
    name_prefix="initial_report",
    rebuild_all=False,
    ## Outcomes
    outcome_start_date=pd.Timestamp("2016-02-01"),
    outcome_end_date=pd.Timestamp("2019-02-01"),
    ## Slices
    slice_name_prefix=None,
    slice_freq=slice_freq, 
    last_slice_date=pd.Timestamp("2016-12-31"), 
    slice_clustering_eligibility_checker=None,
    slice_evaluation_eligibility_checker=slice_evaluation_eligibility_checker, 
    ## Periods
    period_name_prefix=None,
    period_freq=period_freq,
    last_period_date=pd.Timestamp("2016-12-31"), 
    period_eligibility_checker=period_eligibility_checker,
)



# %%
from typing import ClassVar, List, Set, Dict, Tuple, Optional
from dataclasses import dataclass, Field, fields, asdict, astuple, is_dataclass
import pandas as pd
from src.data.persistence_helpers import get_name, get_path, populate

# @dataclass
# class Metadata:
#     freq: 
#     root: str
    
#     rebuild: bool = False


# @dataclass
# class Populator:
    
    
    
#     ### -- Attributes set in __post_init__ -- ###
#     name: str = Field(init=False)


#     @wraps(populator)
#     # `*args` means all the non-keyword arguments to the function wrapped by this decorator;
#     # `**kwargs` means all the keyword arguments (arg=something) in the wrapped function.
#     def populated():

@dataclass
class Team:
    on_first: str = "Who"
    on_second: str = "What"
    on_third: str = "I Don't Know"
    rebuild_all: bool = False
    data: dict = None
    logical_root: Tuple[str] = (".",)
    logical_name: str = "who"

    def __post_init__(self):
        self.new_thingy = "new thingy"
        print(asdict(self))
        print(self.__dict__)

    def you_throw_the_ball_to_who(self, who_picks_it_up: bool = False):
        print("Naturally.")
        if who_picks_it_up is True:
            print("Sometimes his wife picks it up.")

    @populate
    def get_team_data(self, index="position") -> pd.DataFrame:
        data = pd.DataFrame(
            data={"position": ["who", "what"], "first": [1, 2], "second":[3, 4]} 
        ).set_index("position")
        return data
t = Team()







# %%
t.get_team_data(index="position")

# %%
d = pd.DataFrame(
            data={"position": ["who", "what"], "first": [1, 2], "second":[3, 4]} 
        ).set_index("position")

# %%
d = pd.read_feather("D:/repos/evaluation_jp/data/processed/who/who_team_data.feather")

#%%
d

#%%