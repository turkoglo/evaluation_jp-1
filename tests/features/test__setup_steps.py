import numpy as np
import pandas as pd
import pytest
from IPython import display

from evaluation_jp.features import (
    SetupStep,
    SetupSteps,
    LiveRegisterPopulation,
    AgeEligible,
    ClaimCodeEligible,
    ClaimDurationEligible,
    OnLES,
    OnJobPath,
    EligiblePopulation,
)
from evaluation_jp.models import PopulationSliceID, PopulationSlice

# TODO test__NearestKeyDict()


def test__SetupStep(fixture__RandomPopulation):
    results = fixture__RandomPopulation()
    assert isinstance(results, SetupStep)


def test__SetupSteps(fixture__RandomPopulation, fixture__SampleFromPopulation):
    ss = SetupSteps([fixture__RandomPopulation(), fixture__SampleFromPopulation(0.1),])
    results = ss.run()
    assert results.shape == (10, 5)


def test__SetupSteps_with_data_and_data_id(
    fixture__random_date_range_df,
    fixture__RandomPopulation,
    fixture__SampleFromPopulation,
):
    ss = SetupSteps([fixture__RandomPopulation(), fixture__SampleFromPopulation(0.1),])
    results = ss.run(
        data_id={"date": pd.Timestamp("2016-04-01")}, data=fixture__random_date_range_df
    )
    assert results.shape == (10, 5)


@pytest.fixture
def fixture__live_register_population(fixture__population_slice):
    live_register_population = LiveRegisterPopulation(
        columns=[
            "lr_code",
            "clm_comm_date",
            "JobPath_Flag",
            "JobPathHold",
            "date_of_birth",
        ]
    )
    return live_register_population.run(data_id=fixture__population_slice.id)


def test__LiveRegisterPopulation(fixture__live_register_population):
    """Check that number of people on LR == official total per CSO, and correct columns generated
    """
    results = fixture__live_register_population
    assert results.shape == (321373, 5)


# //TODO test__LiveRegisterPopulation__run_with_initial_data


@pytest.fixture
def fixture__date_of_birth_df():
    date_range = pd.date_range(start="1940-01-01", end="1999-12-31", periods=30)
    date_of_birth_df = pd.DataFrame(pd.Series(date_range, name="date_of_birth"))
    return date_of_birth_df


def test__AgeEligible__lt_max(fixture__date_of_birth_df):
    lt_max = AgeEligible(date_of_birth_col="date_of_birth", max_eligible={"years": 60})
    results = lt_max.run(
        PopulationSliceID(date=pd.Timestamp("2016-01-01")),
        data=fixture__date_of_birth_df,
    )
    # 22 out of 30 records have date_of_birth more than 60 years before date
    # Should be 2 columns in results df (date_of_birth and age_eligible)
    assert results.loc[results["age_eligible"]].shape == (22, 2)


def test__AgeEligible__ge_min(fixture__date_of_birth_df):
    ge_min = AgeEligible(date_of_birth_col="date_of_birth", min_eligible={"years": 25})
    results = ge_min.run(
        PopulationSliceID(date=pd.Timestamp("2016-01-01")),
        data=fixture__date_of_birth_df,
    )
    # 22 out of 30 records have date_of_birth more than 60 years before date
    # Should be 2 columns in results df (date_of_birth and age_eligible)
    assert results.loc[results["age_eligible"]].shape == (25, 2)


def test__ClaimCodeEligible():
    data = pd.DataFrame(
        {"lr_code": ["UA", "UB", "UC", "UD", "UE", "UA2", "UB2", "UC2", "UD2", "UE2"]}
    )
    eligible = ClaimCodeEligible(code_col="lr_code", eligible_codes=["UA", "UB"])
    results = eligible.run(
        PopulationSliceID(date=pd.Timestamp("2016-01-01")), data=data
    )
    assert results.loc[results["claim_code_eligible"]].shape == (2, 2)


@pytest.fixture
def fixture__claim_duration_df():
    date_range = pd.date_range(start="2000-01-01", end="2015-12-31", periods=30)
    claim_duration_df = pd.DataFrame(pd.Series(date_range, name="clm_comm_date"))
    return claim_duration_df


def test__ClaimDurationEligible__lt_max(fixture__claim_duration_df):
    eligible = ClaimDurationEligible(
        claim_start_col="clm_comm_date", max_eligible={"years": 5}
    )
    results = eligible.run(
        PopulationSliceID(date=pd.Timestamp("2016-01-01")),
        data=fixture__claim_duration_df,
    )
    assert results.loc[results["claim_duration_eligible"]].shape == (10, 2)


def test__ClaimDurationEligible__ge_min(fixture__claim_duration_df):
    eligible = ClaimDurationEligible(
        claim_start_col="clm_comm_date", min_eligible={"years": 1}
    )
    results = eligible.run(
        PopulationSliceID(date=pd.Timestamp("2016-01-01")),
        data=fixture__claim_duration_df,
    )
    assert results.loc[results["claim_duration_eligible"]].shape == (28, 2)


def test__OnLES(fixture__population_slice, fixture__live_register_population):
    eligible = OnLES(assumed_episode_length={"years": 1})
    results = eligible.run(
        data_id=fixture__population_slice.id, data=fixture__live_register_population
    )
    # Only 1 person in Dec 2015 LR is on the LES file for start of 2016!
    assert results.loc[results["on_les"]].shape == (1, 6)


def test__OnJobPath():
    """Test basic case using just JobPath operational data and not ISTS flag.
    """
    eligible = OnJobPath(assumed_episode_length={"years": 1})
    psid = PopulationSliceID(date=pd.Timestamp("2016-02-01"))
    lrp = LiveRegisterPopulation(columns=["JobPath_Flag", "JobPathHold",])
    results = eligible.run(data_id=psid, data=lrp.run(psid))
    # Manually check number of people on JobPath at start of Feb 2016 == 1441
    assert results.loc[results["on_jobpath"]].shape == (1441, 3)


# //TODO Add test__OnJobPath__ists_only
# //TODO Add test__OnJobPath__operational_and_ists_either
# //TODO Add test__OnJobPath__operational_and_ists_both


def test__EligiblePopulation():
    data = pd.DataFrame(
        {
            "a": [True] * 5 + [False] * 5,
            "b": [True, False] * 5,
            "c": [True] * 8 + [False] * 2,
        }
    )
    expected = data.copy()
    expected["not_c"] = ~expected["c"]
    expected["eligible_population"] = expected[["a", "b", "not_c"]].all(axis="columns")
    expected = expected.drop(["not_c"], axis="columns")

    eligible = EligiblePopulation(
        eligibility_criteria={"a": True, "b": True, "c": False}
    )
    results = eligible.run(data_id=None, data=data)
    print(expected)
    print(results)
    assert results.equals(expected)


def test__all_SetupSteps_for_Population_Slice():

    setup_steps = SetupSteps(
        steps=[
            LiveRegisterPopulation(
                columns=[
                    "lr_code",
                    "clm_comm_date",
                    "JobPath_Flag",
                    "JobPathHold",
                    "date_of_birth",
                ]
            ),
            AgeEligible(date_of_birth_col="date_of_birth", max_eligible={"years": 60}),
            ClaimCodeEligible(code_col="lr_code", eligible_codes=["UA", "UB"]),
            ClaimDurationEligible(
                claim_start_col="clm_comm_date", min_eligible={"years": 1}
            ),
            OnLES(assumed_episode_length={"years": 1}),
            OnJobPath(
                assumed_episode_length={"years": 1},
                use_jobpath_operational_data=True,
                use_ists_claim_data=False,
            ),
            EligiblePopulation(
                eligibility_criteria={
                    "age_eligible": True,
                    "claim_code_eligible": True,
                    "claim_duration_eligible": True,
                    "on_les": False,
                    "on_jobpath": False,
                }
            ),
        ]
    )
    results = PopulationSlice(
        id=PopulationSliceID(date=pd.Timestamp("2016-07-01")), setup_steps=setup_steps
    )
    expected_columns = [
        "JobPathHold",
        "JobPath_Flag",
        "clm_comm_date",
        "lr_code",
        "date_of_birth",
        "age_eligible",
        "claim_code_eligible",
        "claim_duration_eligible",
        "on_les",
        "on_jobpath",
        "eligible_population",
    ]
    assert set(results.data.columns) == set(expected_columns)
    # Manually check how many people are on LR and eligible
    assert len(results.data) == 315654
    assert len(results.data[results.data["eligible_population"]]) == 86240
