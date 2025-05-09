-- 创建数据库
CREATE DATABASE IF NOT EXISTS medical_product;


USE medical_product;

-- 1 药材表 (herbs)
CREATE TABLE IF NOT EXISTS herbs (
    herb_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '药材ID',
    herb_name VARCHAR(100) NOT NULL COMMENT '药材名称',
    specification VARCHAR(100) DEFAULT '' COMMENT '规格：块、粉、粒、干',
    scientific_name VARCHAR(100) COMMENT '学名',
    herb_full_name VARCHAR(201) GENERATED ALWAYS AS (
    CASE 
        WHEN `specification` IS NULL OR TRIM(`specification`) = '' THEN `herb_name` 
        ELSE CONCAT(`herb_name`, '_', `specification`) 
    END
    ) STORED 
    UNIQUE 
    COMMENT '标准化名称（自动生成）',
    unit VARCHAR(20) DEFAULT 'g' COMMENT '单位(g/kg)',
    quality_standard VARCHAR(20) DEFAULT '高级' COMMENT '质量标准',
    storage_condition VARCHAR(50) DEFAULT '常温密封' COMMENT '存储条件',
    shelf_life INT DEFAULT 365 COMMENT '保质期(天)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效药材，1-有效，0-无效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认药材，1-是，0-否',
    UNIQUE KEY uk_herb_name_spec (herb_name, specification) COMMENT '药材名称和规格的唯一约束'
) ENGINE=InnoDB COMMENT='药材基本信息表';

-- 2. 药材库存表 (herb_inventory)
CREATE TABLE IF NOT EXISTS herb_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '库存ID',
    herb_id INT NOT NULL COMMENT '药材ID',
    batch_number VARCHAR(50) NOT NULL COMMENT '批次号',
    quantity DECIMAL(12,3) NOT NULL COMMENT '数量',
    production_date DATE COMMENT '生产日期',
    expiry_date DATE COMMENT '过期日期',
    quality_status ENUM('合格', '不合格', '待检') DEFAULT '待检' COMMENT '质量状态',
    warehouse_location VARCHAR(50) COMMENT '库位',
    locked_quantity DECIMAL(12,3) DEFAULT 0 COMMENT '锁定数量(用于预留)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY fk_herb_id (herb_id) REFERENCES herbs(herb_id) ON UPDATE CASCADE,
    INDEX idx_herb_id (herb_id) COMMENT '药材ID索引',
    INDEX idx_batch_number (batch_number) COMMENT '批次号索引',
    INDEX idx_expiry_date (expiry_date) COMMENT '过期日期索引'
) ENGINE=InnoDB COMMENT='药材库存表';

-- 3. 产品表 (products)
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '产品ID',
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    product_code VARCHAR(50) NOT NULL COMMENT '产品编码',
    specification VARCHAR(100) COMMENT '规格',
    unit VARCHAR(20) NOT NULL COMMENT '单位(盒/瓶/袋等)',
    quality_standard TEXT COMMENT '质量标准',
    description TEXT COMMENT '产品描述',
    shelf_life INT COMMENT '保质期(天)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效产品，1-有效，0-无效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_product_code (product_code) COMMENT '产品编码唯一约束'
) ENGINE=InnoDB COMMENT='产品信息表';

-- 4. 产品组成表 (product_compositions)
CREATE TABLE IF NOT EXISTS product_compositions (
    composition_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '组成ID',
    product_id INT NOT NULL COMMENT '产品ID',
    herb_id INT NOT NULL COMMENT '药材ID',
    quantity DECIMAL(10,3) NOT NULL COMMENT '用量',
    quality_requirement TEXT COMMENT '质量要求',
    processing_method VARCHAR(100) COMMENT '处理方法',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效组成表，1-有效，0-无效',
    FOREIGN KEY fk_product_id (product_id) REFERENCES products(product_id) ON UPDATE CASCADE,
    FOREIGN KEY fk_herb_id (herb_id) REFERENCES herbs(herb_id) ON UPDATE CASCADE,
    UNIQUE KEY uk_product_herb (product_id, herb_id) COMMENT '产品和药材组合的唯一约束'
) ENGINE=InnoDB COMMENT='产品组成表';

-- 5. 药材供应商表 (herb_suppliers)
CREATE TABLE IF NOT EXISTS herb_suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '供应商ID',
    supplier_name VARCHAR(100) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(50) COMMENT '联系人',
    phone VARCHAR(20) COMMENT '联系电话',
    address TEXT COMMENT '地址',
    qualification VARCHAR(100) COMMENT '资质证明',
    quality_rating ENUM('A', 'B', 'C', 'D') COMMENT '质量评级',
    cooperation_status ENUM('合作中', '暂停合作', '终止合作') DEFAULT '合作中' COMMENT '合作状态',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效供应商，1-有效，0-无效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_supplier_name (supplier_name) COMMENT '供应商名称唯一约束'
) ENGINE=InnoDB COMMENT='药材供应商表';

-- 6. 药材入库记录表 (herb_stock_in)
CREATE TABLE IF NOT EXISTS herb_stock_in (
    stock_in_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '入库ID',
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY fk_herb_id (herb_id) REFERENCES herbs(herb_id) ON UPDATE CASCADE,
    FOREIGN KEY fk_supplier_id (supplier_id) REFERENCES herb_suppliers(supplier_id) ON UPDATE CASCADE,
    INDEX idx_herb_id (herb_id) COMMENT '药材ID索引',
    INDEX idx_supplier_id (supplier_id) COMMENT '供应商ID索引',
    INDEX idx_stock_in_date (stock_in_date) COMMENT '入库日期索引'
) ENGINE=InnoDB COMMENT='药材入库记录表';

-- 7. 产品出库记录表 (product_stock_out)
CREATE TABLE IF NOT EXISTS product_stock_out (
    stock_out_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '出库ID',
    product_id INT NOT NULL COMMENT '产品ID',
    quantity INT NOT NULL COMMENT '出库数量',
    recipient VARCHAR(100) COMMENT '收货方',
    stock_out_date DATE NOT NULL COMMENT '出库日期',
    operator VARCHAR(50) NOT NULL COMMENT '操作人',
    batch_number VARCHAR(50) COMMENT '批次号',
    shipping_method VARCHAR(50) COMMENT '运输方式',
    tracking_number VARCHAR(50) COMMENT '运单号',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY fk_product_id (product_id) REFERENCES products(product_id) ON UPDATE CASCADE,
    INDEX idx_product_id (product_id) COMMENT '产品ID索引',
    INDEX idx_stock_out_date (stock_out_date) COMMENT '出库日期索引'
) ENGINE=InnoDB COMMENT='产品出库记录表';

-- 8. 耗材表 (consumables)
CREATE TABLE IF NOT EXISTS consumables (
    consumable_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '耗材ID',
    consumable_name VARCHAR(100) NOT NULL COMMENT '耗材名称',
    consumable_type VARCHAR(50) NOT NULL COMMENT '耗材类型',
    specification VARCHAR(100) COMMENT '规格',
    unit VARCHAR(20) NOT NULL COMMENT '单位',
    standard_quantity INT COMMENT '标准库存量',
    remark TEXT COMMENT '备注',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效耗材，1-有效，0-无效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认耗材，1-是，0-否',
    UNIQUE KEY uk_consumable_name_spec (consumable_name, specification) COMMENT '耗材名称和规格的唯一约束'
) ENGINE=InnoDB COMMENT='耗材信息表';

-- 9. 耗材库存表 (consumable_inventory)
CREATE TABLE IF NOT EXISTS consumable_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '库存ID',
    consumable_id INT NOT NULL COMMENT '耗材ID',
    quantity INT NOT NULL COMMENT '数量',
    warehouse_location VARCHAR(50) COMMENT '库位',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY fk_consumable_id (consumable_id) REFERENCES consumables(consumable_id) ON UPDATE CASCADE,
    INDEX idx_consumable_id (consumable_id) COMMENT '耗材ID索引'
) ENGINE=InnoDB COMMENT='耗材库存表';

-- 10. 耗材供应商表 (consumable_suppliers)
CREATE TABLE IF NOT EXISTS consumable_suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '供应商ID',
    supplier_name VARCHAR(100) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(50) COMMENT '联系人',
    phone VARCHAR(20) COMMENT '联系电话',
    address TEXT COMMENT '地址',
    main_supply VARCHAR(100) COMMENT '主要供应',
    cooperation_status ENUM('合作中', '暂停合作', '终止合作') DEFAULT '合作中' COMMENT '合作状态',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效耗材供应商，1-有效，0-无效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_supplier_name (supplier_name) COMMENT '供应商名称唯一约束'
) ENGINE=InnoDB COMMENT='耗材供应商表';

-- 11. 耗材入库记录表 (consumable_stock_in)
CREATE TABLE IF NOT EXISTS consumable_stock_in (
    stock_in_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '入库ID',
    consumable_id INT NOT NULL COMMENT '耗材ID',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    quantity INT NOT NULL COMMENT '入库数量',
    unit_price DECIMAL(10,2) COMMENT '单价',
    total_amount DECIMAL(12,2) COMMENT '总金额',
    stock_in_date DATE NOT NULL COMMENT '入库日期',
    operator VARCHAR(50) NOT NULL COMMENT '操作人',
    batch_number VARCHAR(50) COMMENT '批次号',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY fk_consumable_id (consumable_id) REFERENCES consumables(consumable_id) ON UPDATE CASCADE,
    FOREIGN KEY fk_supplier_id (supplier_id) REFERENCES consumable_suppliers(supplier_id) ON UPDATE CASCADE,
    INDEX idx_consumable_id (consumable_id) COMMENT '耗材ID索引',
    INDEX idx_supplier_id (supplier_id) COMMENT '供应商ID索引',
    INDEX idx_stock_in_date (stock_in_date) COMMENT '入库日期索引'
) ENGINE=InnoDB COMMENT='耗材入库记录表';

