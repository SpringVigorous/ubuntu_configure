CREATE DATABASE IF NOT EXISTS medical_product;

USE medical_product;

-- 1 药材表 (herbs)
CREATE TABLE IF NOT EXISTS herbs (
    herb_id INT AUTO_INCREMENT PRIMARY KEY,
    herb_name VARCHAR(100) NOT NULL COMMENT '药材名称',
    scientific_name VARCHAR(100) COMMENT '学名',
    specification VARCHAR(100) COMMENT '规格',
    unit VARCHAR(20) NOT NULL COMMENT '单位(克/千克/斤等)',
    quality_standard TEXT COMMENT '质量标准',
    storage_condition VARCHAR(100) COMMENT '存储条件',
    shelf_life INT COMMENT '保质期(天)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效药材',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (herb_name, specification)
) ENGINE=InnoDB COMMENT='药材基本信息表';
-- 2. 药材库存表 (herb_inventory)
CREATE TABLE IF NOT EXISTS herb_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    herb_id INT NOT NULL COMMENT '药材ID',
    batch_number VARCHAR(50) NOT NULL COMMENT '批次号',
    quantity DECIMAL(12,3) NOT NULL COMMENT '数量',
    production_date DATE COMMENT '生产日期',
    expiry_date DATE COMMENT '过期日期',
    quality_status ENUM('合格', '不合格', '待检') DEFAULT '待检' COMMENT '质量状态',
    warehouse_location VARCHAR(50) COMMENT '库位',
    locked_quantity DECIMAL(12,3) DEFAULT 0 COMMENT '锁定数量(用于预留)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (herb_id) REFERENCES herbs(herb_id),
    INDEX (herb_id),
    INDEX (batch_number),
    INDEX (expiry_date)
) ENGINE=InnoDB COMMENT='药材库存表';
-- 3. 产品表 (products)
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    product_code VARCHAR(50) NOT NULL COMMENT '产品编码',
    specification VARCHAR(100) COMMENT '规格',
    unit VARCHAR(20) NOT NULL COMMENT '单位(盒/瓶/袋等)',
    quality_standard TEXT COMMENT '质量标准',
    description TEXT COMMENT '产品描述',
    shelf_life INT COMMENT '保质期(天)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效产品',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (product_code)
) ENGINE=InnoDB COMMENT='产品信息表';
-- 4. 产品组成表 (product_compositions)
CREATE TABLE IF NOT EXISTS product_compositions (
    composition_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL COMMENT '产品ID',
    herb_id INT NOT NULL COMMENT '药材ID',
    quantity DECIMAL(10,3) NOT NULL COMMENT '用量',
    quality_requirement TEXT COMMENT '质量要求',
    processing_method VARCHAR(100) COMMENT '处理方法',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效组成表',
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (herb_id) REFERENCES herbs(herb_id),
    UNIQUE KEY (product_id, herb_id)
) ENGINE=InnoDB COMMENT='产品组成表';
-- 5. 药材供应商表 (herb_suppliers)
CREATE TABLE IF NOT EXISTS herb_suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(50) COMMENT '联系人',
    phone VARCHAR(20) COMMENT '联系电话',
    address TEXT COMMENT '地址',
    qualification VARCHAR(100) COMMENT '资质证明',
    quality_rating ENUM('A', 'B', 'C', 'D') COMMENT '质量评级',
    cooperation_status ENUM('合作中', '暂停合作', '终止合作') DEFAULT '合作中' COMMENT '合作状态',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效供应商',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (supplier_name)
) ENGINE=InnoDB COMMENT='药材供应商表';
-- 6. 药材入库记录表 (herb_stock_in)
CREATE TABLE IF NOT EXISTS herb_stock_in (
    stock_in_id INT AUTO_INCREMENT PRIMARY KEY,
    herb_id INT NOT NULL COMMENT '药材ID',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    batch_number VARCHAR(50) NOT NULL COMMENT '批次号',
    quantity DECIMAL(12,3) NOT NULL COMMENT '入库数量',
    unit_price DECIMAL(10,2) COMMENT '单价',
    total_amount DECIMAL(12,2) COMMENT '总金额',
    production_date DATE COMMENT '生产日期',
    expiry_date DATE COMMENT '过期日期',
    quality_inspection TEXT COMMENT '质检记录',
    inspector VARCHAR(50) COMMENT '检验人',
    stock_in_date DATE NOT NULL COMMENT '入库日期',
    operator VARCHAR(50) NOT NULL COMMENT '操作人',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (herb_id) REFERENCES herbs(herb_id),
    FOREIGN KEY (supplier_id) REFERENCES herb_suppliers(supplier_id),
    INDEX (herb_id),
    INDEX (supplier_id),
    INDEX (stock_in_date)
) ENGINE=InnoDB COMMENT='药材入库记录表';
-- 7. 产品出库记录表 (product_stock_out)
CREATE TABLE IF NOT EXISTS product_stock_out (
    stock_out_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL COMMENT '产品ID',
    quantity INT NOT NULL COMMENT '出库数量',
    recipient VARCHAR(100) COMMENT '收货方',
    stock_out_date DATE NOT NULL COMMENT '出库日期',
    operator VARCHAR(50) NOT NULL COMMENT '操作人',
    batch_number VARCHAR(50) COMMENT '批次号',
    shipping_method VARCHAR(50) COMMENT '运输方式',
    tracking_number VARCHAR(50) COMMENT '运单号',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX (product_id),
    INDEX (stock_out_date)
) ENGINE=InnoDB COMMENT='产品出库记录表';
-- 8. 耗材表 (consumables)
CREATE TABLE IF NOT EXISTS consumables (
    consumable_id INT AUTO_INCREMENT PRIMARY KEY,
    consumable_name VARCHAR(100) NOT NULL COMMENT '耗材名称',
    consumable_type VARCHAR(50) NOT NULL COMMENT '耗材类型',
    specification VARCHAR(100) COMMENT '规格',
    unit VARCHAR(20) NOT NULL COMMENT '单位',
    standard_quantity INT COMMENT '标准库存量',
    remark TEXT COMMENT '备注',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效耗材',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (consumable_name, specification)
) ENGINE=InnoDB COMMENT='耗材信息表';
-- 9. 耗材库存表 (consumable_inventory)
CREATE TABLE IF NOT EXISTS consumable_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    consumable_id INT NOT NULL COMMENT '耗材ID',
    quantity INT NOT NULL COMMENT '数量',
    warehouse_location VARCHAR(50) COMMENT '库位',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (consumable_id) REFERENCES consumables(consumable_id),
    INDEX (consumable_id)
) ENGINE=InnoDB COMMENT='耗材库存表';
-- 10. 耗材供应商表 (consumable_suppliers)
CREATE TABLE IF NOT EXISTS consumable_suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(50) COMMENT '联系人',
    phone VARCHAR(20) COMMENT '联系电话',
    address TEXT COMMENT '地址',
    main_supply VARCHAR(100) COMMENT '主要供应',
    cooperation_status ENUM('合作中', '暂停合作', '终止合作') DEFAULT '合作中' COMMENT '合作状态',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效耗材供应商',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (supplier_name)
) ENGINE=InnoDB COMMENT='耗材供应商表';
-- 11. 耗材入库记录表 (consumable_stock_in)
CREATE TABLE IF NOT EXISTS consumable_stock_in (
    stock_in_id INT AUTO_INCREMENT PRIMARY KEY,
    consumable_id INT NOT NULL COMMENT '耗材ID',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    quantity INT NOT NULL COMMENT '入库数量',
    unit_price DECIMAL(10,2) COMMENT '单价',
    total_amount DECIMAL(12,2) COMMENT '总金额',
    stock_in_date DATE NOT NULL COMMENT '入库日期',
    operator VARCHAR(50) NOT NULL COMMENT '操作人',
    batch_number VARCHAR(50) COMMENT '批次号',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consumable_id) REFERENCES consumables(consumable_id),
    FOREIGN KEY (supplier_id) REFERENCES consumable_suppliers(supplier_id),
    INDEX (consumable_id),
    INDEX (supplier_id),
    INDEX (stock_in_date)
) ENGINE=InnoDB COMMENT='耗材入库记录表';