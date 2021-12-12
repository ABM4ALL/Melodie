from examples.TertiaryModel.db import DB
from examples.TertiaryModel.SUE_analyzer import SEUAnalyzer, SUE_DataCollector, SUETech_DataCollector, \
                                                CarAnalyzer, DeliveryVanAnalyzer, TruckAnalyzer,\
                                                LightingAnalyzer, ServerAnalyzer, ComputerAnalyzer, MonitorAnalyzer, \
                                                PrinterAnalyzer, CopierAnalyzer, ProjectorAnalyzer, InternetConnectionAnalyzer, \
                                                ICTCoolingAnalyzer, InfoScreenAnalyzer,\
                                                CoffeeRoomDishWasherAnalyzer, CoffeeRoomRefrigeratorAnalyzer, CoffeeRoomFreezerAnalyzer,\
                                                CoffeeRoomDrinkAutoSellingMachineAnalyzer, CoffeeRoomSnackAutoSellingMachineAnalyzer, \
                                                CoffeeRoomCoffeeTeaMachineAnalyzer,\
                                                CanteenCookingAnalyzer, CanteenDishGlassWasherAnalyzer,\
                                                CanteenRefrigeratorAnalyzer, CanteenRefrigeratorOtherAnalyzer, CanteenRefrigeratingRoomAnalyzer,\
                                                CanteenFreezerAnalyzer, CanteenFreezerOtherAnalyzer, CanteenFreezingRoomAnalyzer

db_path = "C:\\Users\yus\Dropbox\ABM4ALL\Melodie\examples\TertiaryModel\data\Tertiary.sqlite"
db = DB()
conn = db.create_Connection(db_path)
survey_data = db.read_DataFrame("SharedEndUse_RawData_SectorAdded", conn)
sector_list = list(db.read_DataFrame("Sector", conn)["SECTOR_NAME"])

def print_columns_to_dict():
    columns_list = list(survey_data.columns)
    for column in columns_list:
        print(f'"{column.lower()}": "{column}", ')

def run_SUE_analyzer():
    id_sector_list = [i + 1 for i in range(0, 17)]  # total sector: 17
    analyzer_list: [SEUAnalyzer] = [CarAnalyzer, DeliveryVanAnalyzer, TruckAnalyzer,
                                    LightingAnalyzer, ServerAnalyzer, ComputerAnalyzer, MonitorAnalyzer,
                                    PrinterAnalyzer, CopierAnalyzer, ProjectorAnalyzer, InternetConnectionAnalyzer,
                                    ICTCoolingAnalyzer, InfoScreenAnalyzer,
                                    CoffeeRoomDishWasherAnalyzer, CoffeeRoomRefrigeratorAnalyzer, CoffeeRoomFreezerAnalyzer,
                                    CoffeeRoomDrinkAutoSellingMachineAnalyzer, CoffeeRoomSnackAutoSellingMachineAnalyzer,
                                    CoffeeRoomCoffeeTeaMachineAnalyzer,
                                    CanteenCookingAnalyzer, CanteenDishGlassWasherAnalyzer,
                                    CanteenRefrigeratorAnalyzer, CanteenRefrigeratorOtherAnalyzer, CanteenRefrigeratingRoomAnalyzer,
                                    CanteenFreezerAnalyzer, CanteenFreezerOtherAnalyzer, CanteenFreezingRoomAnalyzer]

    sue_dc = SUE_DataCollector()
    sue_tech_dc = SUETech_DataCollector()
    for id_sector in id_sector_list:
        print("sector: " + sector_list[id_sector - 1])
        for analyzer in analyzer_list:
            ana = analyzer(id_sector)
            ana.adoption_employee_analyzer()
            ana.adoption_floorarea_analyzer()
            ana.tech_analyzer()
            sue_dc.collect_result(ana)
            sue_tech_dc.collect_result(ana)
    sue_dc.save_result(db, conn)
    sue_tech_dc.save_result(db, conn)




if __name__ == "__main__":
    run_SUE_analyzer()








