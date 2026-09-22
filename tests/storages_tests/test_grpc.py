from __future__ import annotations

from datetime import datetime

import pytest

from optuna.storages import BaseStorage
from optuna.storages._grpc.servicer import _from_proto_trial
from optuna.storages._grpc.servicer import _to_proto_trial
from optuna.study._study_direction import StudyDirection
from optuna.testing.storages import STORAGE_MODES
from optuna.testing.storages import StorageSupplier
from optuna.trial import FrozenTrial
from optuna.trial import TrialState


def _test_set_and_get_compatibility(
    storage_set: BaseStorage, storage_get: BaseStorage, values: list[float] | None
) -> None:
    study_id = storage_set.create_new_study(directions=[StudyDirection.MINIMIZE])
    trial_id = storage_set.create_new_trial(study_id)
    assert storage_get.get_trial(trial_id).state == TrialState.RUNNING
    storage_set.set_trial_state_values(trial_id, state=TrialState.COMPLETE, values=values)
    assert storage_get.get_trial(trial_id).state == TrialState.COMPLETE
    assert storage_get.get_trial(trial_id).values == values


@pytest.mark.parametrize("storage_mode", STORAGE_MODES)
@pytest.mark.parametrize("values", [None, [0.0]])
def test_set_and_get_trial_state_values(storage_mode: str, values: list[float] | None) -> None:
    with StorageSupplier(storage_mode) as storage_direct:
        with StorageSupplier("grpc_proxy", base_storage=storage_direct) as storage_grpc_proxy:
            _test_set_and_get_compatibility(storage_grpc_proxy, storage_direct, values)
            _test_set_and_get_compatibility(storage_direct, storage_grpc_proxy, values)


def test_datetime_roundtrip_preserves_local_naive() -> None:
    """Verify that _to_proto_trial/_from_proto_trial preserve naive local datetimes across a round-trip.

    Optuna stores datetimes as naive local datetimes (from datetime.now()). The gRPC
    layer must convert to UTC for wire transport and back to naive local on receipt,
    so the round-tripped value matches the original exactly.
    """
    original = datetime(2025, 6, 15, 14, 30, 45, 123456, tzinfo=None)

    trial = FrozenTrial(
        trial_id=1,
        number=0,
        state=TrialState.RUNNING,
        value=None,
        values=None,
        datetime_start=original,
        datetime_complete=None,
        params={},
        distributions={},
        user_attrs={},
        system_attrs={},
        intermediate_values={},
    )

    proto = _to_proto_trial(trial)
    restored = _from_proto_trial(proto)

    assert restored.datetime_start is not None
    assert restored.datetime_start.tzinfo is None, "Expected naive datetime after round-trip"
    # The naive local time must round-trip unchanged (no timezone offset drift)
    assert restored.datetime_start == original
