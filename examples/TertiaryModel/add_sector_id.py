from examples.TertiaryModel.db import DB

db_path = "C:\\Users\yus\Dropbox\ABM4ALL\Melodie\examples\TertiaryModel\_data\Tertiary.sqlite"
db = DB()
conn = db.create_Connection(db_path)
survey_data = db.read_DataFrame("SharedEndUse_RawData", conn)
sector_list = db.read_DataFrame("Sector", conn)

def identify_sector(group_code, branch_code, sector_code):

    sector_id = None
    sub_sector_id = None
    if group_code == 2 and branch_code == 18:
        if sector_code == 8:
            sector_id = 3
            sub_sector_id = 11
        elif sector_code == 20:
            sector_id = 10
            sub_sector_id = 24
        elif sector_code in [14, 15, 16]:
            sector_id = 11
            sub_sector_id = 25
        elif sector_code in [6, 7, 19]:
            sector_id = 12
            sub_sector_id = 26
        elif sector_code in [1, 2, 3, 4, 9, 10, 11, 12, 13, 17]:
            sector_id = 16
            sub_sector_id = 30
        elif sector_code in [5, 18, 21]:
            sector_id = 17
            sub_sector_id = 34
    else:
        sector_data = sector_list.loc[(sector_list["SURVEY_GROUP_CODE"] == group_code) & (sector_list["SURVEY_BRANCH_CODE"] == branch_code)]
        # sector_id = sector_data.iloc[0]["ID_SECTOR"]
        # sub_sector_id = sector_data.iloc[0]["ID_SUB_SECTOR"]

        try:
            sector_id = sector_data.iloc[0]["ID_SECTOR"]
            sub_sector_id = sector_data.iloc[0]["ID_SUB_SECTOR"]
        except IndexError:
            print((group_code, branch_code, sector_code))
            print(sector_data)

    return [sector_id, sub_sector_id]

def add_sector_id():
    firm_id = []
    sector_id_list = []
    sub_sector_id_list = []
    for row in range(0, len(survey_data)):
        firm_data = survey_data.iloc[row]
        try:
            [firm_sector_id, firm_sub_sector_id] = identify_sector(int(firm_data["SURVEY_GROUP_CODE"]),
                                                                   int(firm_data["SURVEY_BRANCH_CODE"]),
                                                                   int(firm_data["SURVEY_SECTOR_CODE"]))
        except TypeError:
            print("ID_FIRM = " + str(row + 1))
        firm_id.append(row + 1)
        sector_id_list.append(firm_sector_id)
        sub_sector_id_list.append(firm_sub_sector_id)

    survey_data.insert(0, "ID_FIRM", firm_id, True)
    survey_data.insert(1, "ID_SECTOR", sector_id_list, True)
    survey_data.insert(2, "ID_SUB_SECTOR", sub_sector_id_list, True)
    survey_data.to_sql("SharedEndUse_RawData_SectorAdded", conn, index=False, if_exists='replace')

if __name__ == "__main__":

    # survey_data.fillna(0, inplace = True)
    # survey_data.to_sql("to_be_changed", conn)
    # add_sector_id()
    # db.revise_DataType("SharedEndUse_RawData_SectorAdded", "REAL", conn)
    pass