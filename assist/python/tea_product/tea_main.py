from tea_manager import TeaInventorySystem


def main():

    # 初始化系统
    inventory = TeaInventorySystem(
        host='localhost',
        database='medical_product',
        user='SpringFlourish',
        password='137098',
        port=3306,
        pool_size=3
    )
    
    terbs=inventory.get_all_herbs()
    print(terbs)
    # 添加单个耗材
    consumable_id = inventory.add_consumable(
        name="医用口罩",
        consumable_type="防护用品",
        specification="无菌型",
        unit="包",
        standard_quantity=1000
    )

    # 批量添加
    batch_data = [
        {
            "consumable_name": "注射器",
            "consumable_type": "器械",
            "unit": "支",
            "standard_quantity": 5000
        },
        {
            "consumable_name": "消毒液",
            "consumable_type": "消毒剂",
            "specification": "500ml/瓶"
        }
    ]
    success_count = inventory.add_consumables_batch(batch_data)

    # 批量设置默认耗材
    updates = [
        {"consumable_id": 5, "is_default": 1},
        {"consumable_id": 8, "is_default": 1}
    ]
    inventory.update_consumables_batch(updates)
    
    
if __name__ == '__main__':
    main()