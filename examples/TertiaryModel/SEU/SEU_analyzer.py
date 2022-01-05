from examples.TertiaryModel.db import DB
import statsmodels.api as sm
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

db_path = "/examples/TertiaryModel/data/Tertiary.sqlite"
db = DB()
conn = db.create_Connection(db_path)
survey_data = db.read_DataFrame("SharedEndUse_RawData_SectorAdded", conn)
sector_list = list(db.read_DataFrame("Sector", conn)["SECTOR_NAME"])

basic = {
    "id_firm": "ID_FIRM",
    "id_sector": "ID_SECTOR",
    "id_sub_sector": "ID_SUB_SECTOR",
    "survey_firm_id": "SURVEY_FIRM_ID",
    "survey_group_code": "SURVEY_GROUP_CODE",
    "survey_branch_code": "SURVEY_BRANCH_CODE",
    "survey_sector_code": "SURVEY_SECTOR_CODE",
    "location": "LOCATION",
    "rent_out_or_not": "RENT_OUT_OR_NOT",
    "rent_out_area_m2": "RENT_OUT_AREA_M2",
    "employee_count": "EMPLOYEE_COUNT",
}
building = {
    "residential_building_area_m2": "RESIDENTIAL_BUILDING_AREA_M2",
    "residential_building_ageclass": "RESIDENTIAL_BUILDING_AGECLASS",
    "shop_building_area_m2": "SHOP_BUILDING_AREA_M2",
    "shop_building_ageclass": "SHOP_BUILDING_AGECLASS",
    "production_building_area_m2": "PRODUCTION_BUILDING_AREA_M2",
    "production_building_ageclass": "PRODUCTION_BUILDING_AGECLASS",
    "office_building_area_m2": "OFFICE_BUILDING_AREA_M2",
    "office_building_ageclass": "OFFICE_BUILDING_AGECLASS",
    "warehouse_building_area_m2": "WAREHOUSE_BUILDING_AREA_M2",
    "warehouse_building_ageclass": "WAREHOUSE_BUILDING_AGECLASS",
    "other_building_area_m2": "OTHER_BUILDING_AREA_M2",
    "other_building_ageclass": "OTHER_BUILDING_AGECLASS",
    "rent_or_owned": "RENT_OR_OWNED",

    "total_operating_area_m2": "TOTAL_OPERATING_AREA_M2",
    "operation_in_shop_share": "OPERATION_IN_SHOP_SHARE",
    "operation_in_production_share": "OPERATION_IN_PRODUCTION_SHARE",
    "operation_in_office_share": "OPERATION_IN_OFFICE_SHARE",
    "operation_in_warehouse_share": "OPERATION_IN_WAREHOUSE_SHARE",
    "operation_in_basement_share": "OPERATION_IN_BASEMENT_SHARE",
    "operation_in_canteen_share": "OPERATION_IN_CANTEEN_SHARE",
    "operation_in_other_share": "OPERATION_IN_OTHER_SHARE",
}
energy_consumption = {
    "electricity_heating_useage": "ELECTRICITY_HEATING_USEAGE",
    "electricity_heating_quantity": "ELECTRICITY_HEATING_QUANTITY",
    "electricity_heating_unit": "ELECTRICITY_HEATING_UNIT",
    "electricity_heating_cost": "ELECTRICITY_HEATING_COST",
    "electricity_heating_for_heating": "ELECTRICITY_HEATING_FOR_HEATING",
    "electricity_heating_for_hotwater": "ELECTRICITY_HEATING_FOR_HOTWATER",
    "electricity_heating_for_process_heat": "ELECTRICITY_HEATING_FOR_PROCESS_HEAT",

    "electricity_useage": "ELECTRICITY_USEAGE",
    "electricity_quantity": "ELECTRICITY_QUANTITY",
    "electricity_unit": "ELECTRICITY_UNIT",
    "electricity_cost": "ELECTRICITY_COST",
    "electricity_for_heating": "ELECTRICITY_FOR_HEATING",
    "electricity_for_hotwater": "ELECTRICITY_FOR_HOTWATER",
    "electricity_for_process_heat": "ELECTRICITY_FOR_PROCESS_HEAT",

    "natural_gas_useage": "NATURAL_GAS_USEAGE",
    "natural_gas_quantity": "NATURAL_GAS_QUANTITY",
    "natural_gas_unit": "NATURAL_GAS_UNIT",
    "natural_gas_cost": "NATURAL_GAS_COST",
    "natural_gas_for_heating": "NATURAL_GAS_FOR_HEATING",
    "natural_gas_for_hotwater": "NATURAL_GAS_FOR_HOTWATER",
    "natural_gas_for_process_heat": "NATURAL_GAS_FOR_PROCESS_HEAT",

    "bottled_gas_useage": "BOTTLED_GAS_USEAGE",
    "bottled_gas_quantity": "BOTTLED_GAS_QUANTITY",
    "bottled_gas_unit": "BOTTLED_GAS_UNIT",
    "bottled_gas_cost": "BOTTLED_GAS_COST",
    "bottled_gas_for_heating": "BOTTLED_GAS_FOR_HEATING",
    "bottled_gas_for_hotwater": "BOTTLED_GAS_FOR_HOTWATER",
    "bottled_gas_for_process_heat": "BOTTLED_GAS_FOR_PROCESS_HEAT",

    "liquid_gas_useage": "LIQUID_GAS_USEAGE",
    "liquid_gas_quantity": "LIQUID_GAS_QUANTITY",
    "liquid_gas_unit": "LIQUID_GAS_UNIT",
    "liquid_gas_cost": "LIQUID_GAS_COST",
    "liquid_gas_for_heating": "LIQUID_GAS_FOR_HEATING",
    "liquid_gas_for_hotwater": "LIQUID_GAS_FOR_HOTWATER",
    "liquid_gas_for_process_heat": "LIQUID_GAS_FOR_PROCESS_HEAT",

    "heating_oil_useage": "HEATING_OIL_USEAGE",
    "heating_oil_quantity": "HEATING_OIL_QUANTITY",
    "heating_oil_unit": "HEATING_OIL_UNIT",
    "heating_oil_cost": "HEATING_OIL_COST",
    "heating_oil_for_heating": "HEATING_OIL_FOR_HEATING",
    "heating_oil_for_hotwater": "HEATING_OIL_FOR_HOTWATER",
    "heating_oil_for_process_heat": "HEATING_OIL_FOR_PROCESS_HEAT",

    "district_heating_useage": "DISTRICT_HEATING_USEAGE",
    "district_heating_quantity": "DISTRICT_HEATING_QUANTITY",
    "district_heating_unit": "DISTRICT_HEATING_UNIT",
    "district_heating_cost": "DISTRICT_HEATING_COST",
    "district_heating_for_heating": "DISTRICT_HEATING_FOR_HEATING",
    "district_heating_for_hotwater": "DISTRICT_HEATING_FOR_HOTWATER",
    "district_heating_for_process_heat": "DISTRICT_HEATING_FOR_PROCESS_HEAT",

    "hard_coal_useage": "HARD_COAL_USEAGE",
    "hard_coal_quantity": "HARD_COAL_QUANTITY",
    "hard_coal_unit": "HARD_COAL_UNIT",
    "hard_coal_cost": "HARD_COAL_COST",
    "hard_coal_for_heating": "HARD_COAL_FOR_HEATING",
    "hard_coal_for_hotwater": "HARD_COAL_FOR_HOTWATER",
    "hard_coal_for_process_heat": "HARD_COAL_FOR_PROCESS_HEAT",

    "lignite_useage": "LIGNITE_USEAGE",
    "lignite_quantity": "LIGNITE_QUANTITY",
    "lignite_unit": "LIGNITE_UNIT",
    "lignite_cost": "LIGNITE_COST",
    "lignite_for_heating": "LIGNITE_FOR_HEATING",
    "lignite_for_hotwater": "LIGNITE_FOR_HOTWATER",
    "lignite_for_process_heat": "LIGNITE_FOR_PROCESS_HEAT",

    "lump_wood_useage": "LUMP_WOOD_USEAGE",
    "lump_wood_quantity": "LUMP_WOOD_QUANTITY",
    "lump_wood_unit": "LUMP_WOOD_UNIT",
    "lump_wood_cost": "LUMP_WOOD_COST",
    "lump_wood_for_heating": "LUMP_WOOD_FOR_HEATING",
    "lump_wood_for_hotwater": "LUMP_WOOD_FOR_HOTWATER",
    "lump_wood_for_process_heat": "LUMP_WOOD_FOR_PROCESS_HEAT",

    "wood_chips_useage": "WOOD_CHIPS_USEAGE",
    "wood_chips_quantity": "WOOD_CHIPS_QUANTITY",
    "wood_chips_unit": "WOOD_CHIPS_UNIT",
    "wood_chips_cost": "WOOD_CHIPS_COST",
    "wood_chips_for_heating": "WOOD_CHIPS_FOR_HEATING",
    "wood_chips_for_hotwater": "WOOD_CHIPS_FOR_HOTWATER",
    "wood_chips_for_process_heat": "WOOD_CHIPS_FOR_PROCESS_HEAT",

    "other_wood_useage": "OTHER_WOOD_USEAGE",
    "other_wood_quantity": "OTHER_WOOD_QUANTITY",
    "other_wood_unit": "OTHER_WOOD_UNIT",
    "other_wood_cost": "OTHER_WOOD_COST",
    "other_wood_for_heating": "OTHER_WOOD_FOR_HEATING",
    "other_wood_for_hotwater": "OTHER_WOOD_FOR_HOTWATER",
    "other_wood_for_process_heat": "OTHER_WOOD_FOR_PROCESS_HEAT",

    "pellets_useage": "PELLETS_USEAGE",
    "pellets_quantity": "PELLETS_QUANTITY",
    "pellets_unit": "PELLETS_UNIT",
    "pellets_cost": "PELLETS_COST",
    "pellets_for_heating": "PELLETS_FOR_HEATING",
    "pellets_for_hotwater": "PELLETS_FOR_HOTWATER",
    "pellets_for_process_heat": "PELLETS_FOR_PROCESS_HEAT",

    "biogas_useage": "BIOGAS_USEAGE",
    "biogas_quantity": "BIOGAS_QUANTITY",
    "biogas_unit": "BIOGAS_UNIT",
    "biogas_cost": "BIOGAS_COST",
    "biogas_for_heating": "BIOGAS_FOR_HEATING",
    "biogas_for_hotwater": "BIOGAS_FOR_HOTWATER",
    "biogas_for_process_heat": "BIOGAS_FOR_PROCESS_HEAT",

    "unknown_energy_useage": "UNKNOWN_ENERGY_USEAGE",
    "unknown_energy_quantity": "UNKNOWN_ENERGY_QUANTITY",
    "unknown_energy_unit": "UNKNOWN_ENERGY_UNIT",
    "unknown_energy_cost": "UNKNOWN_ENERGY_COST",
    "unknown_energy_for_heating": "UNKNOWN_ENERGY_FOR_HEATING",
    "unknown_energy_for_hotwater": "UNKNOWN_ENERGY_FOR_HOTWATER",
    "unknown_energy_for_process_heat": "UNKNOWN_ENERGY_FOR_PROCESS_HEAT",

    "bill_heating_only_cost": "BILL_HEATING_ONLY_COST",
    "bill_heating_only_for_heat": "BILL_HEATING_ONLY_FOR_HEAT",
    "bill_heating_only_for_hotwater": "BILL_HEATING_ONLY_FOR_HOTWATER",
    "bill_heating_only_for_process_heat": "BILL_HEATING_ONLY_FOR_PROCESS_HEAT",

    "bill_hotwater_only_cost": "BILL_HOTWATER_ONLY_COST",
    "bill_hotwater_only_for_heat": "BILL_HOTWATER_ONLY_FOR_HEAT",
    "bill_hotwater_only_for_hotwater": "BILL_HOTWATER_ONLY_FOR_HOTWATER",
    "bill_hotwater_only_for_process_heat": "BILL_HOTWATER_ONLY_FOR_PROCESS_HEAT",

    "bill_heating_and_hotwater_cost": "BILL_HEATING_AND_HOTWATER_COST",
    "bill_heating_and_hotwater_for_heat": "BILL_HEATING_AND_HOTWATER_FOR_HEAT",
    "bill_heating_and_hotwater_for_hotwater": "BILL_HEATING_AND_HOTWATER_FOR_HOTWATER",
    "bill_heating_and_hotwater_for_process_heat": "BILL_HEATING_AND_HOTWATER_FOR_PROCESS_HEAT",

    "heating_oil_last_year": "HEATING_OIL_LAST_YEAR",
    "heating_oil_refueled": "HEATING_OIL_REFUELED",
    "heating_oil_stock_now": "HEATING_OIL_STOCK_NOW"
}
energy_resource = {
    "hp_usage": "HP_USAGE",
    "hp_size_kw": "HP_SIZE_KW",
    "hp_for_heating": "HP_FOR_HEATING",
    "hp_for_hotwater": "HP_FOR_HOTWATER",
    "hp_for_production": "HP_FOR_PRODUCTION",

    "solar_heat_usage": "SOLAR_HEAT_USAGE",
    "solar_heat_size_m2": "SOLAR_HEAT_SIZE_M2",
    "solar_heat_for_heating": "SOLAR_HEAT_FOR_HEATING",
    "solar_heat_for_hotwater": "SOLAR_HEAT_FOR_HOTWATER",
    "solar_heat_for_production": "SOLAR_HEAT_FOR_PRODUCTION",

    "chp_usage": "CHP_USAGE",
    "chp_size_kw": "CHP_SIZE_KW",
    "chp_for_heating": "CHP_FOR_HEATING",
    "chp_for_hotwater": "CHP_FOR_HOTWATER",
    "chp_for_production": "CHP_FOR_PRODUCTION",

    "waste_heat_recovery_usage": "WASTE_HEAT_RECOVERY_USAGE",
    "waste_heat_recovery_size_kw": "WASTE_HEAT_RECOVERY_SIZE_KW",
    "waste_heat_recovery_for_heating": "WASTE_HEAT_RECOVERY_FOR_HEATING",
    "waste_heat_recovery_for_hotwater": "WASTE_HEAT_RECOVERY_FOR_HOTWATER",
    "waste_heat_recovery_for_production": "WASTE_HEAT_RECOVERY_FOR_PRODUCTION",

    "pv_usage": "PV_USAGE",
    "pv_size_kw": "PV_SIZE_KW",

    "wind_usage": "WIND_USAGE",
    "wind_size_kw": "WIND_SIZE_KW",

    "small_water_plant_size": "SMALL_WATER_PLANT_SIZE",
    "small_water_plant_size_kw": "SMALL_WATER_PLANT_SIZE_KW"
}
end_use = {

    # space heating
    "shop_not_heated_share": "SHOP_NOT_HEATED_SHARE",
    "production_not_heated_share": "PRODUCTION_NOT_HEATED_SHARE",
    "office_not_heated_share": "OFFICE_NOT_HEATED_SHARE",
    "warehouse_not_heated_share": "WAREHOUSE_NOT_HEATED_SHARE",
    "basement_not_heated_share": "BASEMENT_NOT_HEATED_SHARE",
    "canteen_not_heated_share": "CANTEEN_NOT_HEATED_SHARE",
    "other_not_heated_share": "OTHER_NOT_HEATED_SHARE",

    "heating_source_type": "HEATING_SOURCE_TYPE",
    "in_house_heating_tech": "IN_HOUSE_HEATING_TECH",
    "in_house_heating_tech_age": "IN_HOUSE_HEATING_TECH_AGE",
    "auto_temperature_setback_usage": "AUTO_TEMPERATURE_SETBACK_USAGE",

    # hot water
    "hotwater_usage": "HOTWATER_USAGE",
    "hotwater_tech": "HOTWATER_TECH",
    "hotwater_demand_l_per_day": "HOTWATER_DEMAND_L_PER_DAY",
    "hotwater_production_share": "HOTWATER_PRODUCTION_SHARE",
    "hotwater_cleaning_share": "HOTWATER_CLEANING_SHARE",
    "hotwater_hand_washing_share": "HOTWATER_HAND_WASHING_SHARE",
    "hotwater_shower_share": "HOTWATER_SHOWER_SHARE",
    "hotwater_other_share": "HOTWATER_OTHER_SHARE",

    # space cooling
    "shop_air_conditioning_share": "SHOP_AIR_CONDITIONING_SHARE",
    "shop_cooling_share": "SHOP_COOLING_SHARE",
    "shop_fan_share": "SHOP_FAN_SHARE",
    "production_air_conditioning_share": "PRODUCTION_AIR_CONDITIONING_SHARE",
    "production_cooling_share": "PRODUCTION_COOLING_SHARE",
    "production_fan_share": "PRODUCTION_FAN_SHARE",
    "office_air_conditioning_share": "OFFICE_AIR_CONDITIONING_SHARE",
    "office_cooling_share": "OFFICE_COOLING_SHARE",
    "office_fan_share": "OFFICE_FAN_SHARE",
    "warehouse_air_conditioning_share": "WAREHOUSE_AIR_CONDITIONING_SHARE",
    "warehouse_cooling_share": "WAREHOUSE_COOLING_SHARE",
    "warehouse_fan_share": "WAREHOUSE_FAN_SHARE",
    "basement_air_conditioning_share": "BASEMENT_AIR_CONDITIONING_SHARE",
    "basement_cooling_share": "BASEMENT_COOLING_SHARE",
    "basement_fan_share": "BASEMENT_FAN_SHARE",
    "canteen_air_conditioning_share": "CANTEEN_AIR_CONDITIONING_SHARE",
    "canteen_cooling_share": "CANTEEN_COOLING_SHARE",
    "canteen_fan_share": "CANTEEN_FAN_SHARE",
    "other_air_conditioning_share": "OTHER_AIR_CONDITIONING_SHARE",
    "other_cooling_share": "OTHER_COOLING_SHARE",
    "other_fan_share": "OTHER_FAN_SHARE",

    "central_air_conditioner_usage": "CENTRAL_AIR_CONDITIONER_USAGE",
    "central_air_conditioner_size_kw": "CENTRAL_AIR_CONDITIONER_SIZE_KW",
    "central_air_conditioner_hours_per_day": "CENTRAL_AIR_CONDITIONER_HOURS_PER_DAY",
    "central_air_conditioner_days_per_year": "CENTRAL_AIR_CONDITIONER_DAYS_PER_YEAR",
    "mobile_air_conditioner_usage": "MOBILE_AIR_CONDITIONER_USAGE",
    "mobile_air_conditioner_count": "MOBILE_AIR_CONDITIONER_COUNT",
    "mobile_air_conditioner_hour_per_day": "MOBILE_AIR_CONDITIONER_HOUR_PER_DAY",
    "mobile_air_conditioner_days_per_year": "MOBILE_AIR_CONDITIONER_DAYS_PER_YEAR",
    "decentralized_split_air_conditioner_usage": "DECENTRALIZED_SPLIT_AIR_CONDITIONER_USAGE",
    "decentralized_split_air_conditioner_count": "DECENTRALIZED_SPLIT_AIR_CONDITIONER_COUNT",
    "decentralized_split_air_conditioner_hours_per_day": "DECENTRALIZED_SPLIT_AIR_CONDITIONER_HOURS_PER_DAY",
    "decentralized_split_air_conditioner_days_per_year": "DECENTRALIZED_SPLIT_AIR_CONDITIONER_DAYS_PER_YEAR",

    # vehicle
    "car_number": "CAR_NUMBER",
    "car_diesel_liter": "CAR_DIESEL_LITER",
    "car_biodiesel_liter": "CAR_BIODIESEL_LITER",
    "car_gasoline_liter": "CAR_GASOLINE_LITER",
    "car_lpg_liter": "CAR_LPG_LITER",
    "car_other_gas_liter": "CAR_OTHER_GAS_LITER",
    "car_other_gas_kg": "CAR_OTHER_GAS_KG",
    "car_distance_km_per_year": "CAR_DISTANCE_KM_PER_YEAR",
    "car_private_use_share": "CAR_PRIVATE_USE_SHARE",
    "car_power_unit": "CAR_POWER_UNIT",
    "car_power_min": "CAR_POWER_MIN",
    "car_power_max": "CAR_POWER_MAX",

    "delivery_van_number": "DELIVERY_VAN_NUMBER",
    "delivery_van_diesel_liter": "DELIVERY_VAN_DIESEL_LITER",
    "delivery_van_biodiesel_liter": "DELIVERY_VAN_BIODIESEL_LITER",
    "delivery_van_gasoline_liter": "DELIVERY_VAN_GASOLINE_LITER",
    "delivery_van_lpg_liter": "DELIVERY_VAN_LPG_LITER",
    "delivery_van_other_gas_liter": "DELIVERY_VAN_OTHER_GAS_LITER",
    "delivery_van_other_gas_kg": "DELIVERY_VAN_OTHER_GAS_KG",
    "delivery_van_distance_km_per_year": "DELIVERY_VAN_DISTANCE_KM_PER_YEAR",
    "delivery_van_private_use_share": "DELIVERY_VAN_PRIVATE_USE_SHARE",
    "delivery_van_power_unit": "DELIVERY_VAN_POWER_UNIT",
    "delivery_van_power_min": "DELIVERY_VAN_POWER_MIN",
    "delivery_van_power_max": "DELIVERY_VAN_POWER_MAX",

    "truck_number": "TRUCK_NUMBER",
    "truck_diesel_liter": "TRUCK_DIESEL_LITER",
    "truck_biodiesel_liter": "TRUCK_BIODIESEL_LITER",
    "truck_gasoline_liter": "TRUCK_GASOLINE_LITER",
    "truck_lpg_liter": "TRUCK_LPG_LITER",
    "truck_other_gas_liter": "TRUCK_OTHER_GAS_LITER",
    "truck_other_gas_kg": "TRUCK_OTHER_GAS_KG",
    "truck_distance_km_per_year": "TRUCK_DISTANCE_KM_PER_YEAR",
    "truck_private_use_share": "TRUCK_PRIVATE_USE_SHARE",
    "truck_power_unit": "TRUCK_POWER_UNIT",
    "truck_power_min": "TRUCK_POWER_MIN",
    "truck_power_max": "TRUCK_POWER_MAX",

    "total_fuel_cost": "TOTAL_FUEL_COST",
    "electric_or_hybrid_vehicle_usage": "ELECTRIC_OR_HYBRID_VEHICLE_USAGE",
    "electric_or_hybrid_vehicle_number": "ELECTRIC_OR_HYBRID_VEHICLE_NUMBER",
    "electric_or_hybrid_vehicle_distance": "ELECTRIC_OR_HYBRID_VEHICLE_DISTANCE",

    # lighting
    "lighting_system_age": "LIGHTING_SYSTEM_AGE",

    "lighting_brightness_control_usage": "LIGHTING_BRIGHTNESS_CONTROL_USAGE",
    "lighting_brightness_control_type_manual": "LIGHTING_BRIGHTNESS_CONTROL_TYPE_MANUAL",
    "lighting_brightness_control_type_individual_room": "LIGHTING_BRIGHTNESS_CONTROL_TYPE_INDIVIDUAL_ROOM",
    "lighting_brightness_control_type_larger_parts": "LIGHTING_BRIGHTNESS_CONTROL_TYPE_LARGER_PARTS",

    "lighting_total_capacity_kw": "LIGHTING_TOTAL_CAPACITY_KW",
    "lighting_total_capacity_unknown": "LIGHTING_TOTAL_CAPACITY_UNKNOWN",

    "shop_lighting_fluorescent_share": "SHOP_LIGHTING_FLUORESCENT_SHARE",
    "shop_lighting_incandescent_share": "SHOP_LIGHTING_INCANDESCENT_SHARE",
    "shop_lighting_halogen_share": "SHOP_LIGHTING_HALOGEN_SHARE",
    "shop_lighting_led_share": "SHOP_LIGHTING_LED_SHARE",
    "shop_lighting_hours_per_day": "SHOP_LIGHTING_HOURS_PER_DAY",
    "shop_lighting_quality": "SHOP_LIGHTING_QUALITY",

    "production_lighting_fluorescent_share": "PRODUCTION_LIGHTING_FLUORESCENT_SHARE",
    "production_lighting_incandescent_share": "PRODUCTION_LIGHTING_INCANDESCENT_SHARE",
    "production_lighting_halogen_share": "PRODUCTION_LIGHTING_HALOGEN_SHARE",
    "production_lighting_led_share": "PRODUCTION_LIGHTING_LED_SHARE",
    "production_lighting_hours_per_day": "PRODUCTION_LIGHTING_HOURS_PER_DAY",
    "production_lighting_quality": "PRODUCTION_LIGHTING_QUALITY",

    "office_lighting_fluorescent_share": "OFFICE_LIGHTING_FLUORESCENT_SHARE",
    "office_lighting_incandescent_share": "OFFICE_LIGHTING_INCANDESCENT_SHARE",
    "office_lighting_halogen_share": "OFFICE_LIGHTING_HALOGEN_SHARE",
    "office_lighting_led_share": "OFFICE_LIGHTING_LED_SHARE",
    "office_lighting_hours_per_day": "OFFICE_LIGHTING_HOURS_PER_DAY",
    "office_lighting_quality": "OFFICE_LIGHTING_QUALITY",

    "warehouse_lighting_fluorescent_share": "WAREHOUSE_LIGHTING_FLUORESCENT_SHARE",
    "warehouse_lighting_incandescent_share": "WAREHOUSE_LIGHTING_INCANDESCENT_SHARE",
    "warehouse_lighting_halogen_share": "WAREHOUSE_LIGHTING_HALOGEN_SHARE",
    "warehouse_lighting_led_share": "WAREHOUSE_LIGHTING_LED_SHARE",
    "warehouse_lighting_hours_per_day": "WAREHOUSE_LIGHTING_HOURS_PER_DAY",
    "warehouse_lighting_quality": "WAREHOUSE_LIGHTING_QUALITY",

    "basement_lighting_fluorescent_share": "BASEMENT_LIGHTING_FLUORESCENT_SHARE",
    "basement_lighting_incandescent_share": "BASEMENT_LIGHTING_INCANDESCENT_SHARE",
    "basement_lighting_halogen_share": "BASEMENT_LIGHTING_HALOGEN_SHARE",
    "basement_lighting_led_share": "BASEMENT_LIGHTING_LED_SHARE",
    "basement_lighting_hours_per_day": "BASEMENT_LIGHTING_HOURS_PER_DAY",
    "basement_lighting_quality": "BASEMENT_LIGHTING_QUALITY",

    "canteen_lighting_fluorescent_share": "CANTEEN_LIGHTING_FLUORESCENT_SHARE",
    "canteen_lighting_incandescent_share": "CANTEEN_LIGHTING_INCANDESCENT_SHARE",
    "canteen_lighting_halogen_share": "CANTEEN_LIGHTING_HALOGEN_SHARE",
    "canteen_lighting_led_share": "CANTEEN_LIGHTING_LED_SHARE",
    "canteen_lighting_hours_per_day": "CANTEEN_LIGHTING_HOURS_PER_DAY",
    "canteen_lighting_quality": "CANTEEN_LIGHTING_QUALITY",

    "other_lighting_fluorescent_share": "OTHER_LIGHTING_FLUORESCENT_SHARE",
    "other_lighting_incandescent_share": "OTHER_LIGHTING_INCANDESCENT_SHARE",
    "other_lighting_halogen_share": "OTHER_LIGHTING_HALOGEN_SHARE",
    "other_lighting_led_share": "OTHER_LIGHTING_LED_SHARE",
    "other_lighting_hours_per_day": "OTHER_LIGHTING_HOURS_PER_DAY",
    "other_lighting_quality": "OTHER_LIGHTING_QUALITY",

    "fluorescent_average_power_kw": "FLUORESCENT_AVERAGE_POWER_KW",
    "incandescent_average_power_kw": "INCANDESCENT_AVERAGE_POWER_KW",
    "halogen_average_power_kw": "HALOGEN_AVERAGE_POWER_KW",
    "led_average_power_kw": "LED_AVERAGE_POWER_KW",

    "shop_window_lighting_fluorescent_share": "SHOP_WINDOW_LIGHTING_FLUORESCENT_SHARE",
    "shop_window_lighting_incandescent_share": "SHOP_WINDOW_LIGHTING_INCANDESCENT_SHARE",
    "shop_window_lighting_halogen_share": "SHOP_WINDOW_LIGHTING_HALOGEN_SHARE",
    "shop_window_lighting_led_share": "SHOP_WINDOW_LIGHTING_LED_SHARE",
    "shop_window_lighting_hours_per_day": "SHOP_WINDOW_LIGHTING_HOURS_PER_DAY",
    "shop_window_lighting_power_kw": "SHOP_WINDOW_LIGHTING_POWER_KW",

    "facade_advertising_lighting_fluorescent_share": "FACADE_ADVERTISING_LIGHTING_FLUORESCENT_SHARE",
    "facade_advertising_lighting_incandescent_share": "FACADE_ADVERTISING_LIGHTING_INCANDESCENT_SHARE",
    "facade_advertising_lighting_halogen_share": "FACADE_ADVERTISING_LIGHTING_HALOGEN_SHARE",
    "facade_advertising_lighting_led_share": "FACADE_ADVERTISING_LIGHTING_LED_SHARE",
    "facade_advertising_lighting_hours_per_day": "FACADE_ADVERTISING_LIGHTING_HOURS_PER_DAY",
    "facade_advertising_lighting_power_kw": "FACADE_ADVERTISING_LIGHTING_POWER_KW",

    "illuminated_open_space_lighting_fluorescent_share": "ILLUMINATED_OPEN_SPACE_LIGHTING_FLUORESCENT_SHARE",
    "illuminated_open_space_lighting_incandescent_share": "ILLUMINATED_OPEN_SPACE_LIGHTING_INCANDESCENT_SHARE",
    "illuminated_open_space_lighting_halogen_share": "ILLUMINATED_OPEN_SPACE_LIGHTING_HALOGEN_SHARE",
    "illuminated_open_space_lighting_led_share": "ILLUMINATED_OPEN_SPACE_LIGHTING_LED_SHARE",
    "illuminated_open_space_lighting_hours_per_day": "ILLUMINATED_OPEN_SPACE_LIGHTING_HOURS_PER_DAY",
    "illuminated_open_space_lighting_power_kw": "ILLUMINATED_OPEN_SPACE_LIGHTING_POWER_KW",

    # server
    "server_total_count": "SERVER_TOTAL_COUNT",
    "server_total_hours_per_day": "SERVER_TOTAL_HOURS_PER_DAY",
    "server_upto300w_count": "SERVER_UPTO300W_COUNT",
    "server_upto300w_hours_per_day": "SERVER_UPTO300W_HOURS_PER_DAY",
    "server_300to2000w_count": "SERVER_300TO2000W_COUNT",
    "server_300to2000w_hours_per_day": "SERVER_300TO2000W_HOURS_PER_DAY",
    "server_over2000w_count": "SERVER_OVER2000W_COUNT",
    "server_over2000w_hours_per_day": "SERVER_OVER2000W_HOURS_PER_DAY",

    # computer
    "computer_total_count": "COMPUTER_TOTAL_COUNT",
    "computer_total_hours_per_day": "COMPUTER_TOTAL_HOURS_PER_DAY",
    "computer_pc_count": "COMPUTER_PC_COUNT",
    "computer_pc_hours_per_day": "COMPUTER_PC_HOURS_PER_DAY",
    "computer_notebook_count": "COMPUTER_NOTEBOOK_COUNT",
    "computer_notebook_hours_per_day": "COMPUTER_NOTEBOOK_HOURS_PER_DAY",
    "networked_computer_count": "NETWORKED_COMPUTER_COUNT",
    "networked_computer_hours_per_day": "NETWORKED_COMPUTER_HOURS_PER_DAY",

    # monitor
    "monitor_total_count": "MONITOR_TOTAL_COUNT",
    "monitor_total_hours_per_day": "MONITOR_TOTAL_HOURS_PER_DAY",
    "monitor_lcd_count": "MONITOR_LCD_COUNT",
    "monitor_lcd_hours_per_day": "MONITOR_LCD_HOURS_PER_DAY",
    "monitor_other_count": "MONITOR_OTHER_COUNT",
    "monitor_other_hours_per_day": "MONITOR_OTHER_HOURS_PER_DAY",

    # printer
    "printer_total_count": "PRINTER_TOTAL_COUNT",
    "printer_total_hours_per_day": "PRINTER_TOTAL_HOURS_PER_DAY",
    "printer_inkjet_count": "PRINTER_INKJET_COUNT",
    "printer_inkjet_hours_per_day": "PRINTER_INKJET_HOURS_PER_DAY",
    "printer_combination_count": "PRINTER_COMBINATION_COUNT",
    "printer_combination_hours_per_day": "PRINTER_COMBINATION_HOURS_PER_DAY",
    "printer_laser_count": "PRINTER_LASER_COUNT",
    "printer_laser_hours_per_day": "PRINTER_LASER_HOURS_PER_DAY",
    "paper_consumption_printer_inkjet_count_per_month": "PAPER_CONSUMPTION_PRINTER_INKJET_COUNT_PER_MONTH",
    "paper_consumption_printer_other_count_per_month": "PAPER_CONSUMPTION_PRINTER_OTHER_COUNT_PER_MONTH",

    # copier
    "copier_total_count": "COPIER_TOTAL_COUNT",
    "copier_total_hours_per_day": "COPIER_TOTAL_HOURS_PER_DAY",
    "copier_large_count": "COPIER_LARGE_COUNT",
    "copier_large_hours_per_day": "COPIER_LARGE_HOURS_PER_DAY",
    "copier_other_count": "COPIER_OTHER_COUNT",
    "copier_other_hours_per_day": "COPIER_OTHER_HOURS_PER_DAY",

    # projector
    "projector_count": "PROJECTOR_COUNT",
    "projector_hours_per_day": "PROJECTOR_HOURS_PER_DAY",

    # internet connection
    "internet_connection_usage": "INTERNET_CONNECTION_USAGE",
    "lan_connection_usage": "LAN_CONNECTION_USAGE",
    "lan_connection_computer_count": "LAN_CONNECTION_COMPUTER_COUNT",
    "wlan_connection_usage": "WLAN_CONNECTION_USAGE",
    "wlan_connection_computer_count": "WLAN_CONNECTION_COMPUTER_COUNT",

    # ict cooling
    "ict_cooling_area_m2": "ICT_COOLING_AREA_M2",

    # info screen
    "info_screen_upto38cm_count": "INFO_SCREEN_UPTO38CM_COUNT",
    "info_screen_upto38cm_type_pc": "INFO_SCREEN_UPTO38CM_TYPE_PC",
    "info_screen_upto38cm_type_player": "INFO_SCREEN_UPTO38CM_TYPE_PLAYER",
    "info_screen_upto38cm_hours_per_day": "INFO_SCREEN_UPTO38CM_HOURS_PER_DAY",
    "info_screen_38to76cm_count": "INFO_SCREEN_38TO76CM_COUNT",
    "info_screen_38to76cm_type_pc": "INFO_SCREEN_38TO76CM_TYPE_PC",
    "info_screen_38to76cm_type_player": "INFO_SCREEN_38TO76CM_TYPE_PLAYER",
    "info_screen_38to76cm_hours_per_day": "INFO_SCREEN_38TO76CM_HOURS_PER_DAY",
    "info_screen_over76cm_count": "INFO_SCREEN_OVER76CM_COUNT",
    "info_screen_over76cm_type_pc": "INFO_SCREEN_OVER76CM_TYPE_PC",
    "info_screen_over76cm_type_player": "INFO_SCREEN_OVER76CM_TYPE_PLAYER",
    "info_screen_over76cm_hours_per_day": "INFO_SCREEN_OVER76CM_HOURS_PER_DAY",

    # coffee room
    "coffee_room_usage": "COFFEE_ROOM_USAGE",

    # coffee room - dish washer
    "coffee_room_household_dishwasher_count": "COFFEE_ROOM_HOUSEHOLD_DISHWASHER_COUNT",
    "coffee_room_household_dishwasher_efficiency_class": "COFFEE_ROOM_HOUSEHOLD_DISHWASHER_EFFICIENCY_CLASS",
    "coffee_room_household_dishwasher_total_cycles_per_day": "COFFEE_ROOM_HOUSEHOLD_DISHWASHER_TOTAL_CYCLES_PER_DAY",

    # coffee room - refrigerator
    "coffee_room_household_refrigerator_count": "COFFEE_ROOM_HOUSEHOLD_REFRIGERATOR_COUNT",
    "coffee_room_household_refrigerator_efficiency_class": "COFFEE_ROOM_HOUSEHOLD_REFRIGERATOR_EFFICIENCY_CLASS",

    # coffee room - freezer
    "coffee_room_household_freezer_count": "COFFEE_ROOM_HOUSEHOLD_FREEZER_COUNT",
    "coffee_room_household_freezer_efficiency_class": "COFFEE_ROOM_HOUSEHOLD_FREEZER_EFFICIENCY_CLASS",

    # coffee room - auto selling machine
    "coffee_room_drink_auto_machine_count": "COFFEE_ROOM_DRINK_AUTO_MACHINE_COUNT",
    "coffee_room_snack_auto_machine_count": "COFFEE_ROOM_SNACK_AUTO_MACHINE_COUNT",

    # coffee room - coffee and tea machine
    "coffee_or_tea_machine_usage": "COFFEE_OR_TEA_MACHINE_USAGE",
    "coffee_or_tea_machine_not_auto_kitchen_area_count": "COFFEE_OR_TEA_MACHINE_NOT_AUTO_KITCHEN_AREA_COUNT",
    "coffee_or_tea_machine_auto_kitchen_area_count": "COFFEE_OR_TEA_MACHINE_AUTO_KITCHEN_AREA_COUNT",
    "coffee_or_tea_machine_kitchen_area_hours_per_day": "COFFEE_OR_TEA_MACHINE_KITCHEN_AREA_HOURS_PER_DAY",
    "coffee_or_tea_machine_not_auto_among_employee_count": "COFFEE_OR_TEA_MACHINE_NOT_AUTO_AMONG_EMPLOYEE_COUNT",
    "coffee_or_tea_machine_auto_among_employee_count": "COFFEE_OR_TEA_MACHINE_AUTO_AMONG_EMPLOYEE_COUNT",
    "coffee_or_tea_machine_among_employee_hours_per_day": "COFFEE_OR_TEA_MACHINE_AMONG_EMPLOYEE_HOURS_PER_DAY",
    "coffee_or_tea_total_cups_per_year": "COFFEE_OR_TEA_TOTAL_CUPS_PER_YEAR",

    # canteen
    "canteen_usage": "CANTEEN_USAGE",
    "canteen_employee_count": "CANTEEN_EMPLOYEE_COUNT",
    "canteen_open_hours_per_day": "CANTEEN_OPEN_HOURS_PER_DAY",
    "canteen_open_days_per_week": "CANTEEN_OPEN_DAYS_PER_WEEK",
    "canteen_closed_weeks_per_year": "CANTEEN_CLOSED_WEEKS_PER_YEAR",
    "canteen_total_seat_count": "CANTEEN_TOTAL_SEAT_COUNT",

    # canteen: cooking
    "canteen_meal_served_count_per_day": "CANTEEN_MEAL_SERVED_COUNT_PER_DAY",
    "canteen_beer_served_hektoliter_per_year": "CANTEEN_BEER_SERVED_HEKTOLITER_PER_YEAR",
    "canteen_coffee_or_tea_served_count_per_year": "CANTEEN_COFFEE_OR_TEA_SERVED_COUNT_PER_YEAR",
    "canteen_cooking_usage": "CANTEEN_COOKING_USAGE",
    "canteen_cooking_hours_per_day": "CANTEEN_COOKING_HOURS_PER_DAY",

    # canteen: dish and glass washer
    "canteen_glass_washer_count": "CANTEEN_GLASS_WASHER_COUNT",
    "canteen_glass_washer_total_cycle_per_day": "CANTEEN_GLASS_WASHER_TOTAL_CYCLE_PER_DAY",
    "canteen_glass_washer_hotwater_usage": "CANTEEN_GLASS_WASHER_HOTWATER_USAGE",
    "canteen_dish_and_glass_washer_count": "CANTEEN_DISH_AND_GLASS_WASHER_COUNT",
    "canteen_dish_and_glass_washer_total_cycle_per_day": "CANTEEN_DISH_AND_GLASS_WASHER_TOTAL_CYCLE_PER_DAY",
    "canteen_dish_and_glass_washer_hotwater_usage": "CANTEEN_DISH_AND_GLASS_WASHER_HOTWATER_USAGE",
    "canteen_continuous_flow_glass_washer_count": "CANTEEN_CONTINUOUS_FLOW_GLASS_WASHER_COUNT",
    "canteen_continuous_flow_glass_washer_total_cycle_per_day": "CANTEEN_CONTINUOUS_FLOW_GLASS_WASHER_TOTAL_CYCLE_PER_DAY",
    "canteen_continuous_flow_glass_washer_hotwater_usage": "CANTEEN_CONTINUOUS_FLOW_GLASS_WASHER_HOTWATER_USAGE",
    "canteen_continuous_flow_dish_washer_count": "CANTEEN_CONTINUOUS_FLOW_DISH_WASHER_COUNT",
    "canteen_continuous_flow_dish_washer_total_cycle_per_day": "CANTEEN_CONTINUOUS_FLOW_DISH_WASHER_TOTAL_CYCLE_PER_DAY",
    "canteen_continuous_flow_dish_washer_hotwater_usage": "CANTEEN_CONTINUOUS_FLOW_DISH_WASHER_HOTWATER_USAGE",

    # canteen: refrigerator
    "canteen_refrigerator_count": "CANTEEN_REFRIGERATOR_COUNT",
    "canteen_refrigerator_working_length_total_m": "CANTEEN_REFRIGERATOR_WORKING_LENGTH_TOTAL_M",
    "canteen_refrigerator_temperature": "CANTEEN_REFRIGERATOR_TEMPERATURE",
    "canteen_refrigerator_day_usage": "CANTEEN_REFRIGERATOR_DAY_USAGE",
    "canteen_refrigerator_night_usage": "CANTEEN_REFRIGERATOR_NIGHT_USAGE",
    "canteen_refrigerator_lighting_usage": "CANTEEN_REFRIGERATOR_LIGHTING_USAGE",

    "canteen_refrigerator_shelf_count": "CANTEEN_REFRIGERATOR_SHELF_COUNT",
    "canteen_refrigerator_shelf_working_length_total_m": "CANTEEN_REFRIGERATOR_SHELF_WORKING_LENGTH_TOTAL_M",
    "canteen_refrigerator_shelf_temperature": "CANTEEN_REFRIGERATOR_SHELF_TEMPERATURE",
    "canteen_refrigerator_shelf_day_usage": "CANTEEN_REFRIGERATOR_SHELF_DAY_USAGE",
    "canteen_refrigerator_shelf_night_usage": "CANTEEN_REFRIGERATOR_SHELF_NIGHT_USAGE",
    "canteen_refrigerator_shelf_lighting_usage": "CANTEEN_REFRIGERATOR_SHELF_LIGHTING_USAGE",

    "canteen_refrigerator_chest_count": "CANTEEN_REFRIGERATOR_CHEST_COUNT",
    "canteen_refrigerator_chest_working_length_total_m": "CANTEEN_REFRIGERATOR_CHEST_WORKING_LENGTH_TOTAL_M",
    "canteen_refrigerator_chest_temperature": "CANTEEN_REFRIGERATOR_CHEST_TEMPERATURE",
    "canteen_refrigerator_chest_day_usage": "CANTEEN_REFRIGERATOR_CHEST_DAY_USAGE",
    "canteen_refrigerator_chest_night_usage": "CANTEEN_REFRIGERATOR_CHEST_NIGHT_USAGE",
    "canteen_refrigerator_chest_lighting_usage": "CANTEEN_REFRIGERATOR_CHEST_LIGHTING_USAGE",

    "canteen_refrigerator_counter_count": "CANTEEN_REFRIGERATOR_COUNTER_COUNT",
    "canteen_refrigerator_counter_working_length_total_m": "CANTEEN_REFRIGERATOR_COUNTER_WORKING_LENGTH_TOTAL_M",
    "canteen_refrigerator_counter_temperature": "CANTEEN_REFRIGERATOR_COUNTER_TEMPERATURE",
    "canteen_refrigerator_counter_day_usage": "CANTEEN_REFRIGERATOR_COUNTER_DAY_USAGE",
    "canteen_refrigerator_counter_night_usage": "CANTEEN_REFRIGERATOR_COUNTER_NIGHT_USAGE",
    "canteen_refrigerator_counter_lighting_usage": "CANTEEN_REFRIGERATOR_COUNTER_LIGHTING_USAGE",

    # canteen: freezer
    "canteen_freezer_count": "CANTEEN_FREEZER_COUNT",
    "canteen_freezer_working_length_total_m": "CANTEEN_FREEZER_WORKING_LENGTH_TOTAL_M",
    "canteen_freezer_temperature": "CANTEEN_FREEZER_TEMPERATURE",
    "canteen_freezer_day_usage": "CANTEEN_FREEZER_DAY_USAGE",
    "canteen_freezer_night_usage": "CANTEEN_FREEZER_NIGHT_USAGE",
    "canteen_freezer_lighting_usage": "CANTEEN_FREEZER_LIGHTING_USAGE",

    "canteen_freezer_chest_count": "CANTEEN_FREEZER_CHEST_COUNT",
    "canteen_freezer_chest_working_length_total_m": "CANTEEN_FREEZER_CHEST_WORKING_LENGTH_TOTAL_M",
    "canteen_freezer_chest_temperature": "CANTEEN_FREEZER_CHEST_TEMPERATURE",
    "canteen_freezer_chest_day_usage": "CANTEEN_FREEZER_CHEST_DAY_USAGE",
    "canteen_freezer_chest_night_usage": "CANTEEN_FREEZER_CHEST_NIGHT_USAGE",
    "canteen_freezer_chest_lighting_usage": "CANTEEN_FREEZER_CHEST_LIGHTING_USAGE",

    # canteen: referigerating room
    "canteen_refrigerating_room_count": "CANTEEN_REFRIGERATING_ROOM_COUNT",
    "canteen_refrigerating_room_total_area_m2": "CANTEEN_REFRIGERATING_ROOM_TOTAL_AREA_M2",
    "canteen_refrigerating_room_temperature": "CANTEEN_REFRIGERATING_ROOM_TEMPERATURE",
    "canteen_refrigerating_room_capacity_kw": "CANTEEN_REFRIGERATING_ROOM_CAPACITY_KW",

    # canteen: freezing room
    "canteen_freezing_room_count": "CANTEEN_FREEZING_ROOM_COUNT",
    "canteen_freezing_room_total_area_m2": "CANTEEN_FREEZING_ROOM_TOTAL_AREA_M2",
    "canteen_freezing_room_temperature": "CANTEEN_FREEZING_ROOM_TEMPERATURE",
    "canteen_freezing_room_capacity_kw": "CANTEEN_FREEZING_ROOM_CAPACITY_KW",
    "canteen_central_refrigerating_freezing_supply_usage": "CANTEEN_CENTRAL_REFRIGERATING_FREEZING_SUPPLY_USAGE",
}


def run_regression(y_array, x_array):
    if len(x_array) > 5:
        try:
            x_array_addCons = sm.add_constant(x_array)
            est = sm.OLS(y_array, x_array_addCons).fit()
            cons_coef = round(est.params[0], 3)
            x_coef = round(est.params[1], 3)
            cons_pvalue = round(est.pvalues[0], 3)
            x_pvalue = round(est.pvalues[1], 3)
        except IndexError:
            print(y_array)
            print(x_array)
    else:
        cons_coef = 0
        x_coef = 0
        cons_pvalue = 0
        x_pvalue = 0
    return [cons_coef, x_coef, cons_pvalue, x_pvalue]

def transform_X_to_value(value_list, X_string, X_value) -> np.array:
    value_update = []
    for item in value_list:
        if item == X_string:
            value_update.append(X_value)
        else:
            value_update.append(0)
    return np.array(value_update)

class SEUAnalyzer(ABC):

    def __init__(self, id_sector=None):

        self.id_sector: int = id_sector
        self.sector_name = sector_list[self.id_sector - 1]
        self.end_use: str = ""
        self.tech_info: list = [] # energy_carrier, power, power_unit, adoption_share
        self.adoption_unit: str = ""
        self.duration_unit: str = ""
        self.sector_sample: pd.DataFrame = self.set_sector_sample()
        self.sector_sample_size: int = len(self.sector_sample)
        self.sector_sample_selected: pd.DataFrame = self.sector_sample_selection()
        self.sector_sample_selected_size: int = len(self.sector_sample_selected)
        self.penetration_rate: float = round(self.sector_sample_selected_size / self.sector_sample_size, 3)
        self.adoption: np.array = self.set_adoption()
        self.duration: float = self.set_duration()

        self.adoption_employee_cons_coef: float = 0
        self.adoption_employee_employee_coef: float = 0
        self.adoption_employee_cons_pvalue: float = 0
        self.adoption_employee_employee_pvalue: float = 0
        self.adoption_employee_average: float = 0

        self.adoption_floorarea_cons_coef: float = 0
        self.adoption_floorarea_floorarea_coef: float = 0
        self.adoption_floorarea_cons_pvalue: float = 0
        self.adoption_floorarea_floorarea_pvalue: float = 0
        self.adoption_floorarea_average: float = 0

    def set_sector_sample(self) -> pd.DataFrame:
        if self.id_sector == None:
            return survey_data
        else:
            return survey_data.loc[survey_data["ID_SECTOR"] == self.id_sector]

    @abstractmethod
    def sector_sample_selection(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def set_adoption(self) -> np.array:
        pass

    @abstractmethod
    def set_duration(self) -> float:
        pass

    @abstractmethod
    def tech_analyzer(self) -> None:
        pass

    def adoption_employee_analyzer(self) -> None:
        employee = self.sector_sample_selected[basic["employee_count"]].values
        [self.adoption_employee_cons_coef, self.adoption_employee_employee_coef,
         self.adoption_employee_cons_pvalue, self.adoption_employee_employee_pvalue] = run_regression(self.adoption, employee)
        try:
            self.adoption_employee_average = round(self.adoption.sum() / employee.sum(), 3)
        except ValueError:
            self.adoption_employee_average = self.adoption.sum() / employee.sum()

    def adoption_floorarea_analyzer(self) -> None:
        floorarea = self.sector_sample_selected[building["total_operating_area_m2"]].values
        [self.adoption_floorarea_cons_coef, self.adoption_floorarea_floorarea_coef,
         self.adoption_floorarea_cons_pvalue, self.adoption_floorarea_floorarea_pvalue] = run_regression(self.adoption, floorarea)
        try:
            self.adoption_floorarea_average = round(self.adoption.sum() / floorarea.sum(), 3)
        except ValueError:
            self.adoption_floorarea_average = self.adoption.sum() / floorarea.sum()

    def print_info(self):
        print("sector_sample_size = " + str(self.sector_sample_size))
        print("sector_sample_selected_size = " + str(self.sector_sample_selected_size))
        print("penetration_rate = " + str(self.penetration_rate))
        print("adoption_sum = " + str(self.adoption.sum()))
        print("duration = " + str(self.duration))

        print("adoption_employee_cons_coef = " + str(self.adoption_employee_cons_coef))
        print("adoption_employee_employee_coef = " + str(self.adoption_employee_employee_coef))
        print("adoption_employee_cons_pvalue = " + str(self.adoption_employee_cons_pvalue))
        print("adoption_employee_employee_pvalue = " + str(self.adoption_employee_employee_pvalue))
        print("adoption_employee_average = " + str(self.adoption_employee_average))

        print("adoption_floorarea_cons_coef = " + str(self.adoption_floorarea_cons_coef))
        print("adoption_floorarea_floorarea_coef = " + str(self.adoption_floorarea_floorarea_coef))
        print("adoption_floorarea_cons_pvalue = " + str(self.adoption_floorarea_cons_pvalue))
        print("adoption_floorarea_floorarea_pvalue = " + str(self.adoption_floorarea_floorarea_pvalue))
        print("adoption_floorarea_average = " + str(self.adoption_floorarea_average))
        print()

class CarAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "car"
        self.adoption_unit: str = "count"
        self.duration_unit: str = "km/year"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["car_number"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["car_number"]].values
        return adoption

    def set_duration(self) -> float:
        duration = self.sector_sample_selected[end_use["car_distance_km_per_year"]].values.sum()
        return round(duration/self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name = "car"
        tech_selected = self.sector_sample_selected[(self.sector_sample[end_use["car_number"]] > 0)]
        tech_energy_carrier = "mix"
        tech_energy_consumption_kwh = 10 * tech_selected[end_use["car_diesel_liter"]].values.sum() + \
                                      9.1 * tech_selected[end_use["car_gasoline_liter"]].values.sum() + \
                                      9.08 * tech_selected[end_use["car_biodiesel_liter"]].values.sum() + \
                                      6.9 * (tech_selected[end_use["car_lpg_liter"]].values +
                                             tech_selected[end_use["car_other_gas_liter"]].values).sum() + \
                                      12.87 * tech_selected[end_use["car_other_gas_kg"]].values.sum()
        tech_power = round(tech_energy_consumption_kwh/tech_selected[end_use["car_distance_km_per_year"]].values.sum(), 3)
        tech_power_unit = "kWh/km"
        tech_adoption_share = 1
        self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class DeliveryVanAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "delivery_van"
        self.adoption_unit: str = "count"
        self.duration_unit: str = "km/year"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["delivery_van_number"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["delivery_van_number"]].values
        return adoption

    def set_duration(self) -> float:
        duration = self.sector_sample_selected[end_use["delivery_van_distance_km_per_year"]].values.sum()
        return round(duration/self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name = "delivery_van"
        tech_selected = self.sector_sample_selected[(self.sector_sample[end_use["delivery_van_number"]] > 0)]
        tech_energy_carrier = "mix"
        tech_energy_consumption_kwh = 10 * tech_selected[end_use["delivery_van_diesel_liter"]].values.sum() + \
                                      9.1 * tech_selected[end_use["delivery_van_gasoline_liter"]].values.sum() + \
                                      9.08 * tech_selected[end_use["delivery_van_biodiesel_liter"]].values.sum() + \
                                      6.9 * (tech_selected[end_use["delivery_van_lpg_liter"]].values +
                                             tech_selected[end_use["delivery_van_other_gas_liter"]].values).sum() + \
                                      12.87 * tech_selected[end_use["delivery_van_other_gas_kg"]].values.sum()
        tech_power = round(tech_energy_consumption_kwh / tech_selected[end_use["delivery_van_distance_km_per_year"]].values.sum(), 3)
        tech_power_unit = "kWh/km"
        tech_adoption_share = 1
        self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class TruckAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "truck"
        self.adoption_unit: str = "count"
        self.duration_unit: str = "km/year"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["truck_number"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["truck_number"]].values
        return adoption

    def set_duration(self) -> float:
        duration = self.sector_sample_selected[end_use["truck_distance_km_per_year"]].values.sum()
        return round(duration/self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name = "truck"
        tech_selected = self.sector_sample_selected[(self.sector_sample[end_use["truck_number"]] > 0)]
        tech_energy_carrier = "mix"
        tech_energy_consumption_kwh = 10 * tech_selected[end_use["truck_diesel_liter"]].values.sum() + \
                                      9.1 * tech_selected[end_use["truck_gasoline_liter"]].values.sum() + \
                                      9.08 * tech_selected[end_use["truck_biodiesel_liter"]].values.sum() + \
                                      6.9 * (tech_selected[end_use["truck_lpg_liter"]].values +
                                             tech_selected[end_use["truck_other_gas_liter"]].values).sum() + \
                                      12.87 * tech_selected[end_use["truck_other_gas_kg"]].values.sum()
        tech_power = round(tech_energy_consumption_kwh / tech_selected[end_use["truck_distance_km_per_year"]].values.sum(), 3)
        tech_power_unit = "kWh/km"
        tech_adoption_share = 1
        self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class LightingAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "lighting"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["fluorescent_average_power_kw"]] > 0) |
                                                        (self.sector_sample[end_use["incandescent_average_power_kw"]] > 0) |
                                                        (self.sector_sample[end_use["halogen_average_power_kw"]] > 0) |
                                                        (self.sector_sample[end_use["led_average_power_kw"]] > 0)]

        return sector_sample_selected

    def set_adoption(self) -> np.array:
        fluorescent_adoption = self.sector_sample_selected[end_use["fluorescent_average_power_kw"]].values/0.01235
        incandescent_adoption = self.sector_sample_selected[end_use["incandescent_average_power_kw"]].values/0.06
        halogen_adoption = self.sector_sample_selected[end_use["halogen_average_power_kw"]].values/0.02424
        LED_adoption = self.sector_sample_selected[end_use["led_average_power_kw"]].values/0.00355
        adoption = fluorescent_adoption + incandescent_adoption + halogen_adoption + LED_adoption
        return adoption

    def set_duration(self) -> float:
        areas = ["shop", "production", "office", "warehouse", "basement", "canteen", "other"]
        hours_per_day_list = [("UNTER4STD", 4), ("4BIS8STD", 6), ("UEBER8STD", 8)]

        area_hours_list = []
        area_operating_share_list = []
        for area in areas:

            area_lighting_hours = area + "_lighting_hours_per_day"
            firm_total_num = 0
            area_total_hours = 0
            for hours_per_day in hours_per_day_list:
                firm_num = len(self.sector_sample_selected[self.sector_sample_selected[end_use[area_lighting_hours]] == hours_per_day[0]])
                area_hour = firm_num * hours_per_day[1]
                firm_total_num += firm_num
                area_total_hours += area_hour
            if firm_total_num == 0:
                area_hours_list.append(0)
            else:
                area_average_hour = area_total_hours/firm_total_num
                area_hours_list.append(area_average_hour)

            area_operating_share = "operation_in_" + area + "_share"
            area_operating_share_list.append(self.sector_sample_selected[building[area_operating_share]].values.mean())

        hours_sum = 0
        for area_num in range(0, len(areas)):
            hours_sum += area_hours_list[area_num] * area_operating_share_list[area_num]
        duration = hours_sum/np.array(area_operating_share_list).sum()

        return round(duration, 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["fluorescent", "incandescent", "halogen", "led"]
        tech_power_list = [0.01235, 0.06, 0.02424, 0.00355]
        fluorescent_adoption = (self.sector_sample_selected[end_use["fluorescent_average_power_kw"]].values / 0.01235).sum()
        incandescent_adoption = (self.sector_sample_selected[end_use["incandescent_average_power_kw"]].values / 0.06).sum()
        halogen_adoption = (self.sector_sample_selected[end_use["halogen_average_power_kw"]].values / 0.02424).sum()
        LED_adoption = (self.sector_sample_selected[end_use["led_average_power_kw"]].values / 0.00355).sum()
        tech_adoption_array = np.array([fluorescent_adoption, incandescent_adoption, halogen_adoption, LED_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech + "_bulb"
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class ServerAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "server"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["server_total_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["server_total_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["server_upto300w_count"]].values * self.sector_sample_selected[end_use["server_upto300w_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["server_300to2000w_count"]].values * self.sector_sample_selected[end_use["server_300to2000w_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["server_over2000w_count"]].values * self.sector_sample_selected[end_use["server_over2000w_hours_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["server_upto300", "server_300to2000", "server_over2000"]
        tech_power_list = [-9999, -9999, -9999]
        server_upto300_adoption = (self.sector_sample_selected[end_use["server_upto300w_count"]].values).sum()
        server_300to2000_adoption = (self.sector_sample_selected[end_use["server_300to2000w_count"]].values).sum()
        server_over2000_adoption = (self.sector_sample_selected[end_use["server_over2000w_count"]].values).sum()
        tech_adoption_array = np.array([server_upto300_adoption, server_300to2000_adoption, server_over2000_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class ComputerAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "computer"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["computer_total_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["computer_total_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["computer_notebook_count"]].values * self.sector_sample_selected[end_use["computer_notebook_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["computer_pc_count"]].values * self.sector_sample_selected[end_use["computer_pc_hours_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["computer_pc", "computer_notebook"]
        tech_power_list = [-9999, -9999]
        computer_pc_adoption = (self.sector_sample_selected[end_use["computer_pc_count"]].values).sum()
        computer_notebook_adoption = (self.sector_sample_selected[end_use["computer_notebook_count"]].values).sum()
        tech_adoption_array = np.array([computer_pc_adoption, computer_notebook_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class MonitorAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "monitor"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["monitor_total_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["monitor_total_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["monitor_lcd_count"]].values * self.sector_sample_selected[end_use["monitor_lcd_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["monitor_other_count"]].values * self.sector_sample_selected[end_use["monitor_other_hours_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["monitor_lcd", "monitor_other"]
        tech_power_list = [-9999, -9999]
        monitor_lcd_adoption = (self.sector_sample_selected[end_use["monitor_lcd_count"]].values).sum()
        monitor_other_adoption = (self.sector_sample_selected[end_use["monitor_other_count"]].values).sum()
        tech_adoption_array = np.array([monitor_lcd_adoption, monitor_other_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class PrinterAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "printer"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["printer_total_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["printer_total_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["printer_inkjet_count"]].values * self.sector_sample_selected[end_use["printer_inkjet_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["printer_combination_count"]].values * self.sector_sample_selected[end_use["printer_combination_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["printer_laser_count"]].values * self.sector_sample_selected[end_use["printer_laser_hours_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["printer_inkjet", "printer_combination", "printer_laser"]
        tech_power_list = [-9999, -9999, -9999]
        printer_inkjet_adoption = (self.sector_sample_selected[end_use["printer_inkjet_count"]].values).sum()
        printer_combination_adoption = (self.sector_sample_selected[end_use["printer_combination_count"]].values).sum()
        printer_laser_adoption = (self.sector_sample_selected[end_use["printer_laser_count"]].values).sum()
        tech_adoption_array = np.array([printer_inkjet_adoption, printer_combination_adoption, printer_laser_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class CopierAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "copier"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["copier_total_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["copier_total_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["copier_large_count"]].values * self.sector_sample_selected[end_use["copier_large_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["copier_other_count"]].values * self.sector_sample_selected[end_use["copier_other_hours_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["copier_large", "copier_other"]
        tech_power_list = [-9999, -9999]
        copier_large_adoption = (self.sector_sample_selected[end_use["copier_large_count"]].values).sum()
        copier_other_adoption = (self.sector_sample_selected[end_use["copier_other_count"]].values).sum()
        tech_adoption_array = np.array([copier_large_adoption, copier_other_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class ProjectorAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "projector"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["projector_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["projector_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["projector_count"]].values * self.sector_sample_selected[end_use["projector_hours_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["projector"]
        tech_power_list = [-9999]
        projector_adoption = (self.sector_sample_selected[end_use["projector_count"]].values).sum()
        tech_adoption_array = np.array([projector_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class InternetConnectionAnalyzer(SEUAnalyzer):
    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "internet_connection"
        self.adoption_unit = "count of connected computers"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["lan_connection_computer_count"]] > 0) |
                                                        (self.sector_sample[end_use["wlan_connection_computer_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = (self.sector_sample_selected[end_use["lan_connection_computer_count"]].values +
                    self.sector_sample_selected[end_use["wlan_connection_computer_count"]].values)
        return adoption

    def set_duration(self) -> float:
        duration = 24
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["internet_connection", "electricity", -9999, "kWh", 1])

class ICTCoolingAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "ICT_cooling"
        self.adoption_unit = "m2"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["ict_cooling_area_m2"]] > 0]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["ict_cooling_area_m2"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["ict_cooling", "electricity", -9999, "kWh", 1])

class InfoScreenAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "info_screen"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["info_screen_upto38cm_count"]] > 0) |
                                                        (self.sector_sample[end_use["info_screen_38to76cm_count"]] > 0) |
                                                        (self.sector_sample[end_use["info_screen_over76cm_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = (self.sector_sample_selected[end_use["info_screen_upto38cm_count"]].values +
                    self.sector_sample_selected[end_use["info_screen_38to76cm_count"]].values +
                    self.sector_sample_selected[end_use["info_screen_over76cm_count"]].values)
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["info_screen_upto38cm_count"]].values * self.sector_sample_selected[end_use["info_screen_upto38cm_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["info_screen_38to76cm_count"]].values * self.sector_sample_selected[end_use["info_screen_38to76cm_hours_per_day"]].values +
                    self.sector_sample_selected[end_use["info_screen_over76cm_count"]].values * self.sector_sample_selected[end_use["info_screen_over76cm_hours_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["info_screen_upto38cm", "info_screen_38to76cm", "info_screen_over76cm"]
        tech_power_list = [-9999, -9999, -9999]
        info_screen_upto38cm_adoption = (self.sector_sample_selected[end_use["info_screen_upto38cm_count"]].values).sum()
        info_screen_38to76cm_adoption = (self.sector_sample_selected[end_use["info_screen_38to76cm_count"]].values).sum()
        info_screen_over76cm_adoption = (self.sector_sample_selected[end_use["info_screen_over76cm_count"]].values).sum()
        tech_adoption_array = np.array([info_screen_upto38cm_adoption, info_screen_38to76cm_adoption, info_screen_over76cm_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class CoffeeRoomDishWasherAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "coffee_room_dish_washer"
        self.adoption_unit = "count"
        self.duration_unit = "cycle/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["coffee_room_household_dishwasher_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["coffee_room_household_dishwasher_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["coffee_room_household_dishwasher_count"]].values *
                    self.sector_sample_selected[end_use["coffee_room_household_dishwasher_total_cycles_per_day"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        self.tech_info.append(["coffee_room_dish_washer", "electricity", -9999, "kWh", 1])

class CoffeeRoomRefrigeratorAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "coffee_room_refrigerator"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["coffee_room_household_refrigerator_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["coffee_room_household_refrigerator_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["coffee_room_refrigerator", "electricity", -9999, "kWh", 1])

class CoffeeRoomFreezerAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "coffee_room_freezer"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["coffee_room_household_freezer_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["coffee_room_household_freezer_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["coffee_room_freezer", "electricity", -9999, "kWh", 1])

class CoffeeRoomDrinkAutoSellingMachineAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "coffee_room_drink_auto_selling_machine"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["coffee_room_drink_auto_machine_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["coffee_room_drink_auto_machine_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["coffee_room_drink_auto_selling_machine", "electricity", -9999, "kWh", 1])

class CoffeeRoomSnackAutoSellingMachineAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "coffee_room_snack_auto_selling_machine"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["coffee_room_snack_auto_machine_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["coffee_room_snack_auto_machine_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["coffee_room_snack_auto_selling_machine", "electricity", -9999, "kWh", 1])

class CoffeeRoomCoffeeTeaMachineAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "coffee_room_coffee_or_tea_machine"
        self.adoption_unit = "count"
        self.duration_unit = "cup/day"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["coffee_or_tea_machine_usage"]] == "JA"]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["coffee_or_tea_machine_auto_kitchen_area_count"]].values + \
                   self.sector_sample_selected[end_use["coffee_or_tea_machine_not_auto_kitchen_area_count"]].values + \
                   self.sector_sample_selected[end_use["coffee_or_tea_machine_auto_among_employee_count"]].values + \
                   self.sector_sample_selected[end_use["coffee_or_tea_machine_not_auto_among_employee_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["coffee_or_tea_total_cups_per_year"]].values).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["coffee_or_tea_machine_auto", "coffee_or_tea_machine_not_auto"]
        tech_power_list = [-9999, -9999]
        coffee_or_tea_machine_auto_adoption = (self.sector_sample_selected[end_use["coffee_or_tea_machine_auto_kitchen_area_count"]].values +
                                               self.sector_sample_selected[end_use["coffee_or_tea_machine_auto_among_employee_count"]].values).sum()
        coffee_or_tea_machine_not_auto_adoption = (self.sector_sample_selected[end_use["coffee_or_tea_machine_not_auto_kitchen_area_count"]].values +
                                                   self.sector_sample_selected[end_use["coffee_or_tea_machine_not_auto_among_employee_count"]].values).sum()
        tech_adoption_array = np.array([coffee_or_tea_machine_auto_adoption, coffee_or_tea_machine_not_auto_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class CanteenCookingAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_cooking"
        self.adoption_unit = "meal/day"
        self.duration_unit = "day/year"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["canteen_cooking_usage"]] == "WIRDZUBEREITET"]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["canteen_meal_served_count_per_day"]].values
        return adoption

    def set_duration(self) -> float:
        duration = (self.sector_sample_selected[end_use["canteen_open_days_per_week"]].values *
                    (52.14 - self.sector_sample_selected[end_use["canteen_closed_weeks_per_year"]].values)).sum()
        return round(duration, 3)

    def tech_analyzer(self) -> None:
        self.tech_info.append(["canteen_cooking", "mix", -9999, "kWh", 1])

class CanteenDishGlassWasherAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_dish_glass_washer"
        self.adoption_unit = "count"
        self.duration_unit = "cycle/year"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["canteen_glass_washer_count"]] > 0) |
                                                        (self.sector_sample[end_use["canteen_dish_and_glass_washer_count"]] > 0) |
                                                        (self.sector_sample[end_use["canteen_continuous_flow_glass_washer_count"]] > 0) |
                                                        (self.sector_sample[end_use["canteen_continuous_flow_dish_washer_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = (self.sector_sample_selected[end_use["canteen_glass_washer_count"]].values +
                    self.sector_sample_selected[end_use["canteen_dish_and_glass_washer_count"]].values +
                    self.sector_sample_selected[end_use["canteen_continuous_flow_glass_washer_count"]].values +
                    self.sector_sample_selected[end_use["canteen_continuous_flow_dish_washer_count"]].values)
        return adoption

    def set_duration(self) -> float:
        duration = ((self.sector_sample_selected[end_use["canteen_glass_washer_total_cycle_per_day"]].values +
                     self.sector_sample_selected[end_use["canteen_dish_and_glass_washer_total_cycle_per_day"]].values +
                     self.sector_sample_selected[end_use["canteen_continuous_flow_glass_washer_total_cycle_per_day"]].values +
                     self.sector_sample_selected[end_use["canteen_continuous_flow_dish_washer_total_cycle_per_day"]].values) *
                    (self.sector_sample_selected[end_use["canteen_open_days_per_week"]].values *
                     (52.14 - self.sector_sample_selected[end_use["canteen_closed_weeks_per_year"]].values))).sum()
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["canteen_glass_washer", "canteen_dish_and_glass_washer",
                          "canteen_continuous_flow_glass_washer", "canteen_continuous_flow_dish_washer"]
        tech_power_list = [-9999, -9999, -9999, -9999]
        canteen_glass_washer_adoption = (self.sector_sample_selected[end_use["canteen_glass_washer_count"]].values).sum()
        canteen_dish_and_glass_washer_adoption = (self.sector_sample_selected[end_use["canteen_dish_and_glass_washer_count"]].values).sum()
        canteen_continuous_flow_glass_washer_adoption = (self.sector_sample_selected[end_use["canteen_continuous_flow_glass_washer_count"]].values).sum()
        canteen_continuous_flow_dish_washer_adoption = (self.sector_sample_selected[end_use["canteen_continuous_flow_dish_washer_count"]].values).sum()
        tech_adoption_array = np.array([canteen_glass_washer_adoption, canteen_dish_and_glass_washer_adoption,
                                        canteen_continuous_flow_glass_washer_adoption, canteen_continuous_flow_dish_washer_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class CanteenRefrigeratorAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_refrigerator"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["canteen_refrigerator_count"]] > 0]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["canteen_refrigerator_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24.0
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["canteen_refrigerator", "electricity", -9999, "kWh", 1])

class CanteenRefrigeratorOtherAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_refrigerator_other"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[(self.sector_sample[end_use["canteen_refrigerator_shelf_count"]] > 0) |
                                                        (self.sector_sample[end_use["canteen_refrigerator_chest_count"]] > 0) |
                                                        (self.sector_sample[end_use["canteen_refrigerator_counter_count"]] > 0)]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = (self.sector_sample_selected[end_use["canteen_refrigerator_shelf_count"]].values +
                    self.sector_sample_selected[end_use["canteen_refrigerator_chest_count"]].values +
                    self.sector_sample_selected[end_use["canteen_refrigerator_counter_count"]].values)
        return adoption

    def set_duration(self) -> float:
        shelf_hours = transform_X_to_value(self.sector_sample_selected[end_use["canteen_refrigerator_shelf_day_usage"]].to_list(), "X", 12) + \
                      transform_X_to_value(self.sector_sample_selected[end_use["canteen_refrigerator_shelf_night_usage"]].to_list(), "X", 12)
        chest_hours = transform_X_to_value(self.sector_sample_selected[end_use["canteen_refrigerator_chest_day_usage"]].to_list(), "X", 12) + \
                      transform_X_to_value(self.sector_sample_selected[end_use["canteen_refrigerator_chest_night_usage"]].to_list(), "X", 12)
        counter_hours = transform_X_to_value(self.sector_sample_selected[end_use["canteen_refrigerator_counter_day_usage"]].to_list(), "X", 12) + \
                        transform_X_to_value(self.sector_sample_selected[end_use["canteen_refrigerator_counter_night_usage"]].to_list(), "X", 12)
        try:
            duration = (self.sector_sample_selected[end_use["canteen_refrigerator_shelf_count"]].values * shelf_hours +
                        self.sector_sample_selected[end_use["canteen_refrigerator_chest_count"]].values * chest_hours +
                        self.sector_sample_selected[end_use["canteen_refrigerator_counter_count"]].values * counter_hours).sum()
        except ValueError:
            duration = 0
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        tech_name_list = ["canteen_refrigerator_shelf", "canteen_refrigerator_chest", "canteen_refrigerator_counter"]
        tech_power_list = [-9999, -9999, -9999]
        canteen_refrigerator_shelf_adoption = (self.sector_sample_selected[end_use["canteen_refrigerator_shelf_count"]].values).sum()
        canteen_refrigerator_chest_adoption = (self.sector_sample_selected[end_use["canteen_refrigerator_chest_count"]].values).sum()
        canteen_refrigerator_counter_adoption = (self.sector_sample_selected[end_use["canteen_refrigerator_counter_count"]].values).sum()
        tech_adoption_array = np.array([canteen_refrigerator_shelf_adoption, canteen_refrigerator_chest_adoption,
                                        canteen_refrigerator_counter_adoption])
        tech_adoption_share_array = tech_adoption_array/tech_adoption_array.sum()

        for count, tech in enumerate(tech_name_list):
            tech_name = tech
            tech_energy_carrier = "electricity"
            tech_power = tech_power_list[count]
            tech_power_unit = "kW"
            tech_adoption_share = round(tech_adoption_share_array[count], 3)
            self.tech_info.append([tech_name, tech_energy_carrier, tech_power, tech_power_unit, tech_adoption_share])

class CanteenRefrigeratingRoomAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_refrigerating_room"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["canteen_refrigerating_room_count"]] > 0]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["canteen_refrigerating_room_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24.0
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["canteen_refrigerating_room", "electricity", -9999, "kWh", 1])

class CanteenFreezerAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_freezer"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["canteen_freezer_count"]] > 0]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["canteen_freezer_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24.0
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["canteen_freezer", "electricity", -9999, "kWh", 1])

class CanteenFreezerOtherAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_freezer_other"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["canteen_freezer_chest_count"]] > 0]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["canteen_freezer_chest_count"]].values
        return adoption

    def set_duration(self) -> float:
        chest_hours = transform_X_to_value(self.sector_sample_selected[end_use["canteen_freezer_chest_day_usage"]].to_list(), "X", 12) + \
                      transform_X_to_value(self.sector_sample_selected[end_use["canteen_freezer_chest_night_usage"]].to_list(), "X", 12)
        try:
            duration = (self.sector_sample_selected[end_use["canteen_freezer_chest_count"]].values * chest_hours).sum()
        except ValueError:
            duration = 0
        return round(duration / self.adoption.sum(), 3)

    def tech_analyzer(self) -> None:
        self.tech_info.append(["canteen_freezer_other", "electricity", -9999, "kWh", 1])

class CanteenFreezingRoomAnalyzer(SEUAnalyzer):

    def sector_sample_selection(self) -> pd.DataFrame:
        self.end_use: str = "canteen_freezing_room"
        self.adoption_unit = "count"
        self.duration_unit = "hour/day"
        sector_sample_selected = self.sector_sample.loc[self.sector_sample[end_use["canteen_freezing_room_count"]] > 0]
        return sector_sample_selected

    def set_adoption(self) -> np.array:
        adoption = self.sector_sample_selected[end_use["canteen_freezing_room_count"]].values
        return adoption

    def set_duration(self) -> float:
        duration = 24.0
        return duration

    def tech_analyzer(self) -> None:
        self.tech_info.append(["canteen_freezing_room", "electricity", -9999, "kWh", 1])

class SUE_DataCollector:

    def __init__(self):
        self.result = []
        self.result_columns = ["SECTOR_ID", "SECTOR",
                               "END_USE", "ADOPTION_UNIT", "DURATION_UNIT",
                               "SECTOR_SAMPLE_SIZE", "SECTOR_SAMPLE_SELECTED_SIZE", "PENETRATION_RATE",
                               "ADOPTION_EMPLOYEE_CONS_COEF", "ADOPTION_EMPLOYEE_EMPLOYEE_COEF",
                               "ADOPTION_EMPLOYEE_CONS_PVALUE", "ADOPTION_EMPLOYEE_EMPLOYEE_PVALUE",
                               "ADOPTION_PER_EMPLOYEE",
                               "ADOPTION_FLOORAREA_CONS_COEF", "ADOPTION_FLOORAREA_FLOORAREA_COEF",
                               "ADOPTION_FLOORAREA_CONS_PVALUE", "ADOPTION_FLOORAREA_FLOORAREA_PVALUE",
                               "ADOPTION_PER_FLOORAREA",
                               "DURATION"]

    def collect_result(self, analyzer: SEUAnalyzer) -> None:
        self.result.append([analyzer.id_sector, analyzer.sector_name,
                            analyzer.end_use, analyzer.adoption_unit, analyzer.duration_unit,
                            analyzer.sector_sample_size, analyzer.sector_sample_selected_size, analyzer.penetration_rate,
                            analyzer.adoption_employee_cons_coef, analyzer.adoption_employee_employee_coef,
                            analyzer.adoption_employee_cons_pvalue, analyzer.adoption_employee_employee_pvalue,
                            analyzer.adoption_employee_average,
                            analyzer.adoption_floorarea_cons_coef, analyzer.adoption_floorarea_floorarea_coef,
                            analyzer.adoption_floorarea_cons_pvalue, analyzer.adoption_floorarea_floorarea_pvalue,
                            analyzer.adoption_floorarea_average,
                            analyzer.duration])

    def save_result(self, db:DB, conn):
        db.write_DataFrame(self.result, "Regression", self.result_columns, conn)

class SUETech_DataCollector:

    def __init__(self):
        self.result = []
        self.result_columns = ["SECTOR_ID", "SECTOR", "END_USE",
                               "TECH", "ENERGY_CARRIER", "POWER", "POWER_UNIT", "TECH_SHARE"]

    def collect_result(self, analyzer: SEUAnalyzer) -> None:
        for tech_data in analyzer.tech_info:
            self.result.append([analyzer.id_sector, analyzer.sector_name, analyzer.end_use] + tech_data)

    def save_result(self, db:DB, conn):
        db.write_DataFrame(self.result, "Tech_info", self.result_columns, conn)



