from examples.TertiaryModel.db import DB

db_path = "C:\\Users\yus\Dropbox\ABM4ALL\Melodie\examples\TertiaryModel\data\Tertiary.sqlite"
db = DB()
conn = db.create_Connection(db_path)
done = db.read_DataFrame("SharedEndUse_RawData_SectorAdded", conn)


def append_ids(survey_firm_id,
               id_firm, id_sector, id_sub_sector,
               id_survey_group, id_survey_branch, id_survey_sector,
               employee, floor_area):

    row = done.loc[done["SURVEY_FIRM_ID"] == survey_firm_id].iloc[0]
    id_firm.append(row["ID_FIRM"])
    id_sector.append(row["ID_SECTOR"])
    id_sub_sector.append(row["ID_SUB_SECTOR"])
    id_survey_group.append(row["SURVEY_GROUP_CODE"])
    id_survey_branch.append(row["SURVEY_BRANCH_CODE"])
    id_survey_sector.append(row["SURVEY_SECTOR_CODE"])
    employee.append(row["EMPLOYEE_COUNT"])
    floor_area.append(row["TOTAL_OPERATING_AREA_M2"])


if __name__ == "__main__":

    table_list = ["G1", "G3", "G4",
                  "G5_1", "G5_2", "G5_3",
                  "G6_1", "G6_2", "G6_3",
                  "G7_1", "G7_2", "G7_3",
                  "G8", "G9", "G10", "G12"]
    for table in table_list:
        print("current_table = " + table)
        target = db.read_DataFrame(table, conn)
        target = target.rename(columns={"Nr.": "SURVEY_FIRM_ID"})
        id_firm = []
        id_sector = []
        id_sub_sector = []
        id_survey_group = []
        id_survey_branch = []
        id_survey_sector = []
        employee = []
        floor_area = []
        for id_row in range(len(target)):
            survey_firm_id = target.iloc[id_row]["SURVEY_FIRM_ID"]
            append_ids(survey_firm_id,
                       id_firm, id_sector, id_sub_sector,
                       id_survey_group, id_survey_branch, id_survey_sector,
                       employee, floor_area)

        target.insert(1, "TOTAL_OPERATING_AREA_M2", floor_area, True)
        target.insert(1, "EMPLOYEE_COUNT", employee, True)
        target.insert(1, "SURVEY_SECTOR_CODE", id_survey_sector, True)
        target.insert(1, "SURVEY_BRANCH_CODE", id_survey_branch, True)
        target.insert(1, "SURVEY_GROUP_CODE", id_survey_group, True)
        target.insert(0, "ID_SUB_SECTOR", id_sub_sector, True)
        target.insert(0, "ID_SECTOR", id_sector, True)
        target.insert(0, "ID_FIRM", id_firm, True)
        target.to_sql(table + "_SectorAdded", conn, index=False, if_exists='replace')



























