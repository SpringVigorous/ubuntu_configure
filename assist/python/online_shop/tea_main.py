from tea_manager import TeaInventorySystem


def main():

    # 初始化系统
    inventory = TeaInventorySystem(
        host='localhost',
        database='tea_inventory',
        user='root',
        password='password'
    )

    # 添加新药材
    herb_id = inventory.add_herb(
        name="菊花",
        scientific_name="Chrysanthemum morifolium",
        specification="特级",
        unit="克"
    )

    # 添加配方
    formula_id = inventory.add_formula(
        name="菊花茶",
        code="JHC-001",
        total_weight=5.0,
        description="清热去火菊花茶"
    )

    # 添加配方成分
    inventory.add_formula_component(
        formula_id=formula_id,
        herb_id=herb_id,
        weight=5.0,
        requirements="选用完整无破损的菊花"
    )

    # 药材入库
    inventory.stock_in_herb(
        herb_id=herb_id,
        quantity=1000,
        batch_number="JH2023001",
        operator="张三",
        production_date="2023-01-15",
        expiry_date="2024-01-15"
    )

    # 获取所有药材（用于前端下拉选择）
    herbs = inventory.get_all_herbs()
    print("可用药材:", herbs)
    # 撤销最后一次操作
    if inventory.undo_last_operation():
        print("成功撤销最后一次操作")