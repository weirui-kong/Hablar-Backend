create database if not exists harblar;
use harblar;
-- 创建key表
CREATE TABLE if not exists `key` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `key` CHAR(32) NOT NULL,
    `balance` INT NOT NULL,
    `created_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    `last_balance_update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 创建翻译记录表trs_log
CREATE TABLE `trs_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `key_id` INT,
    `source_language_code` VARCHAR(5) NOT NULL,
    `target_language_code` VARCHAR(5) NOT NULL,
    `source_text` TEXT NOT NULL,
    `result_text` TEXT NOT NULL,
    `audio_file_path` VARCHAR(512),
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (`key_id`) REFERENCES `key`(`id`)
);

-- 创建key的使用记录表key_log
CREATE TABLE if not exists `key_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `key_id` INT,
    `trs_id` INT,
    `change` INT NOT NULL,
    `success` BOOLEAN NOT NULL,
    `ip` VARCHAR(45) NOT NULL,
    `device_operator` VARCHAR(128),
    `fyi` VARCHAR(32),
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (`key_id`) REFERENCES `key`(`id`),
    FOREIGN KEY (`trs_id`) REFERENCES `trs_log`(`id`)
);

-- 创建支持的语言表
create table lang
(
    id               int auto_increment
        primary key,
    lang_code        varchar(8)   not null comment 'ISO Language Code, e.g.: zh-CN, en-US',
    native_lang_name varchar(128) not null,
    voice_code       varchar(32)  not null
);