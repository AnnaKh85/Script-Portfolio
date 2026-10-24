from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional
_LOCAL_TYPES = {"LOCAL", "LOCAL_CHAPTER_19"}
_EXCLUDED_STATUSES = {"NEW", "XML_PARSING_ERROR"}
def _nested(source: Optional[Dict], path: str, default=None) -> Any:
    if not isinstance(source, dict):
        return default
    cur = source
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur if cur is not None else default


def _str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _decimal(value: Any) -> Decimal:
    s = str(value).strip() if value is not None and str(value).strip() != "" else "0.0"
    return Decimal(s).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _local_total_price(local_ctx: Dict, price_kind: str) -> Decimal:
    paths = [
        f"summary.building.{price_kind}.value",
        f"summary.mounting.{price_kind}.value",
        f"summary.equipment.{price_kind}.value",
        f"summary.otherPrice.{price_kind}.value",
    ]
    return sum(_decimal(_nested(local_ctx, p)) for p in paths)

class TestPackageConsistency:
    def test_package_id_in_structure(self, interdoc_structure: Dict, package_id: str):
            structure_pid = _str(interdoc_structure.get("packageId"))
            print(f"\nПроверка packageId: структура={structure_pid}, ожидается={package_id}")
            assert structure_pid == package_id, (
                f"packageId в структуре не совпадает: {structure_pid} != {package_id}"
            )
            print(f"✅ packageId совпадает: {structure_pid}")


    def test_excluded_statuses_not_in_structure(
            self,
            estimates_list: List[Dict],
            estimate_db_contexts: Dict[str, Dict],
        ):
            print(
                f"\nПроверка: estimates со статусом {_EXCLUDED_STATUSES} "
                f"не должны присутствовать в структуре"
            )
            violations = []
            for est in estimates_list:
                eid = str(est.get("estimateId", ""))
                db = estimate_db_contexts.get(eid, {})
                db_status = db.get("status", "")
                print(f"  estimateId={eid}, status в БД={db_status}")
                if db_status in _EXCLUDED_STATUSES:
                    violations.append(
                        f"estimateId={eid} status={db_status} не должен присутствовать в структуре"
                    )
            assert not violations, "\n".join(violations)
            print(f"✅ Все estimates имеют допустимые статусы")


    def test_estimate_type_matches_db(
            self,
            estimates_list: List[Dict],
            estimate_db_contexts: Dict[str, Dict],
        ):
            print("\nПроверка поля type для каждого estimate:")
            print(f"{'estimateId':<40} | {'структура':<20} | {'БД':<20} | результат")
            print("-" * 95)
            errors = []
            for est in estimates_list:
                eid = str(est.get("estimateId", ""))
                structure_type = est.get("type")
                db_type = estimate_db_contexts.get(eid, {}).get("type")
                match = _str(structure_type) == _str(db_type)
                mark = "✅" if match else "❌"
                print(f"{eid:<40} | {_str(structure_type):<20} | {_str(db_type):<20} | {mark}")
                if not match:
                    errors.append(f"estimateId={eid}: type={structure_type} != DB={db_type}")
            assert not errors, "\n".join(errors)


    def test_estimate_name_matches_db(
            self,
            estimates_list: List[Dict],
            estimate_db_contexts: Dict[str, Dict],
        ):
            print("\nПроверка поля name (report_name) для каждого estimate:")
            print(f"{'estimateId':<40} | {'name в структуре':<50} | {'report_name в БД':<50} | результат")
            print("-" * 150)
            errors = []
            for est in estimates_list:
                eid = str(est.get("estimateId", ""))
                structure_name = _str(est.get("name"))
                db_name = _str(estimate_db_contexts.get(eid, {}).get("report_name"))
                match = structure_name == db_name
                mark = "✅" if match else "❌"
                print(f"{eid:<40} | {structure_name:<50} | {db_name:<50} | {mark}")
                if not match:
                    errors.append(f"estimateId={eid}: name='{structure_name}' != report_name='{db_name}'")
            assert not errors, "\n".join(errors)


    def test_local_summary_cost_fields(
            self,
            estimates_list: List[Dict],
            estimate_db_contexts: Dict[str, Dict],
        ):
            cost_fields = [
                ("summary.building.base.value", "summary.building.base.value"),
                ("summary.building.current.value", "summary.building.current.value"),
                ("summary.mounting.base.value", "summary.mounting.base.value"),
                ("summary.mounting.current.value", "summary.mounting.current.value"),
                ("summary.equipment.base.value", "summary.equipment.base.value"),
                ("summary.equipment.current.value", "summary.equipment.current.value"),
                ("summary.other.base.value", "summary.otherPrice.base.value"),
                ("summary.other.current.value", "summary.otherPrice.current.value"),
            ]
            print("\nПроверка стоимостных полей summary для ЛСР:")
            print(f"{'estimateId':<40} | {'поле структуры':<30} | {'структура':>12} | {'БД':>12} | результат")
            print("-" * 105)
            errors = []
            for est in estimates_list:
                if est.get("type") not in _LOCAL_TYPES:
                    continue
                eid = str(est.get("estimateId", ""))
                data = est.get("data") or {}
                db_lctx = estimate_db_contexts.get(eid, {}).get("local_ctx") or {}
                for struct_path, db_path in cost_fields:
                    s_val = _decimal(_nested(data, struct_path))
                    d_val = _decimal(_nested(db_lctx, db_path))
                    match = s_val == d_val
                    mark = "✅" if match else "❌"
                    print(f"{eid:<40} | {struct_path:<30} | {s_val:>12} | {d_val:>12} | {mark}")
                    if not match:
                        errors.append(
                            f"estimateId={eid}: {struct_path}={s_val} != DB {db_path}={d_val}"
                        )
            assert not errors, "\n".join(errors)


    def test_local_summary_total_price(
            self,
            estimates_list: List[Dict],
            estimate_db_contexts: Dict[str, Dict],
        ):
            print("\nПроверка totalPrice для ЛСР (= сумма округлённых компонент):")
            print(f"{'estimateId':<40} | {'уровень цен':<10} | {'структура':>12} | {'ожидается':>12} | результат")
            print("-" * 90)
            errors = []
            for est in estimates_list:
                if est.get("type") not in _LOCAL_TYPES:
                    continue
                eid = str(est.get("estimateId", ""))
                data = est.get("data") or {}
                db_lctx = estimate_db_contexts.get(eid, {}).get("local_ctx") or {}
                for price_kind in ("base", "current"):
                    s_total = _decimal(_nested(data, f"summary.totalPrice.{price_kind}.value"))
                    expected = _local_total_price(db_lctx, price_kind)
                    match = s_total == expected
                    mark = "✅" if match else "❌"
                    print(f"{eid:<40} | {price_kind:<10} | {s_total:>12} | {expected:>12} | {mark}")
                    if not match:
                        errors.append(
                            f"estimateId={eid}: totalPrice.{price_kind}={s_total} != сумма компонент={expected}"
                        )
            assert not errors, "\n".join(errors)
