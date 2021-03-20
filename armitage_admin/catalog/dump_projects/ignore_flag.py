import urllib.parse

import pymongo

def refer_collection():
  # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database
  mycol = mydb["simplified_dump_min"]  # creates a collection
  # mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol


def set_ignore_flag(profile_id_list):
    mycol = refer_collection()
    for id_a in profile_id_list:
        mycol.update_one({'_id': id_a}, {'$set': {'ignore_flag':'1'}})


def unset_ignore_flag(profile_id_list):
    mycol = refer_collection()
    for id_a in profile_id_list:
        mycol.update_one({'_id': id_a}, {'$set': {'ignore_flag':'0'}})


def update_by_filter(filter):
    mycol = refer_collection()

    # myquery = {"link": {"$regex": filter}}

    # mydoc = list(mycol.find(myquery
    #                    , {
    #                         '_id': 1
    #                         , 'ignore_flag': 1
    #                    }))

    result = mycol.update_many(
        {"link": {"$regex": filter}},
        # {"company_status": {"$regex": filter}},
        {"$set": {"ignore_flag": "1"}}
    )

    print(result.matched_count)

    # for x in result:
    #     print(x)


def update_by_company_status(filter):
    mycol = refer_collection()

    # myquery = {"link": {"$regex": filter}}

    # mydoc = list(mycol.find(myquery
    #                    , {
    #                         '_id': 1
    #                         , 'ignore_flag': 1
    #                    }))

    result = mycol.update_many(
        {"company_status": {"$regex": filter}},
        {"$set": {"ignore_flag": "1"}}
    )

    print(result.matched_count)

    # for x in result:
    #     print(x)



def get_by_company_status(filter):
    mycol = refer_collection()

    myquery = {"company_status": {"$regex": filter}}

    result = list(mycol.find(myquery))

    for x in result:
        print(x)

    print("Done")


def test(filter):
    mycol = refer_collection()

    # myquery = {"company_type_dnb": {"$elemMatch": {"$regex": 'Public'}}}

    # result = list(mycol.find(myquery))
    #
    # for x in result:
    #     print(x)
    #
    # print("Done")
    result = mycol.update_many(
        {"company_type_dnb": {"$elemMatch": {"$regex": 'Public'}}},
        {"$set": {"ignore_flag": "1"}}
    )

    print(result.matched_count)

#
# update_by_filter("/.*edu.*/")
# update_by_filter("/.*org.*/")
# update_by_filter("/.*gov.*/")
# update_by_filter("/.*abc.net.*/")

# get_by_filter("/.*org.*/")

# update_by_company_status("Public")
# get_by_company_status("Public.*/")

# update_by_filter("/.*abc.net.*/")
# update_by_filter("/.*probonoaustralia.com.au.*/")
# update_by_filter("/.*www.adelaidenow.com.au.*/")
# update_by_filter("/.*prwire.com.au.*/")
# update_by_filter("/.*www.healthcareit.com.au.*/")
# update_by_filter("/.*time.com.*/")
# update_by_filter("/.*equityhealthj.biomedcentral.com.*/")
# update_by_filter("/.*coastcommunitynews.com.au.*/")
# update_by_filter("/.*global.foreignaffairs.co.nz.*/")
# update_by_filter("/.*www.theaustralian.com.au.*/")
# update_by_filter("/.*www.themorningbulletin.com.au.*/")
# update_by_filter("/.*www.9news.com.au.*/")
# update_by_filter("/.*www.theguardian.com.*/")
# update_by_filter("/.*www.nationaltribune.com.au.*/")
# update_by_filter("/.*www.agedcareinsite.com.au.*/")
# update_by_filter("/.*www.smh.com.au.*/")
# update_by_filter("/.*www.lawyersweekly.com.au.*/")
# update_by_filter("/.*www.themandarin.com.au.*/")
# update_by_filter("/.*news.sap.com.*/")
# update_by_filter("/.*www.zdnet.com.*/")
# update_by_filter("/.*www.anzics.com.au.*/")
# update_by_filter("/.*bizedge.co.nz.*/")
# update_by_filter("/.*www.thesenior.com.au.*/")
# update_by_filter("/.*www.sbs.com.au.*/")
# update_by_filter("/.*idm.net.au.*/")
# update_by_filter("/.*www.cio.com.*/")
update_by_filter("/.*www.anz.com.*/")
update_by_filter("/.*findojobs.com.*/")
update_by_filter("/.*www.anz.com.au/personal.*/")
update_by_filter("/.*www.sage.com.*/")
update_by_filter("/.*www.mypcorp.com.*/")
update_by_filter("/.*www.theaccessgroup.com.au.*/")
update_by_filter("/.*anzdmc.com.au.*/")
update_by_filter("/.*www.telstrahealth.com.*/")
update_by_filter("/.*www.naati.com.au.*/")
update_by_filter("/.*www.farah.net.au.*/")
update_by_filter("/.*www.ironbark.com.au.*/")
update_by_filter("/.*www.simprogroup.com.*/")
update_by_filter("/.*academic.oup.com/journals.*/")
update_by_filter("/.*www.hill-rom.com.au.*/")
update_by_filter("/.*www.miragenews.com.*/")
update_by_filter("/.*www.ranzcr.com.*/")
update_by_filter("/.*visability.applyfirst.net.*/")
update_by_filter("/.*www.bupa.com.au.*/")
update_by_filter("/.*www2.deloitte.com.*/")
update_by_filter("/.*engie.com.au.*/")
update_by_filter("/.*www.charteredaccountantsanz.com.*/")
update_by_filter("/.*jobs.laimoon.com.*/")
update_by_filter("/.*home.mypcorp.com.*/")
update_by_filter("/.*www.pwc.com.au.*/")
update_by_filter("/.*www.nuance.com/index.html.*/")
update_by_filter("/.*www.clubmatestravel.com.*/")
update_by_filter("/.*www.honeywell.com.*/")
update_by_filter("/.*www.accenture.com/us-en.*/")
update_by_filter("/.*www.ethicaljobs.com.au.*/")
update_by_filter("/.*www.reckon.com.*/")
update_by_filter("/.*seekjobsaustralia.com.*/")
update_by_filter("/.*www.solutionmindsconsulting.com.au.*/")
update_by_filter("/.*www.gladstoneobserver.com.au.*/")
update_by_filter("/.*www.anzap.com.au.*/")
update_by_filter("/.*anziif.com.*/")
update_by_filter("/.*www.jobx.com.au.*/")
update_by_filter("/.*www.jobsforyouth.com.au.*/")
# test("")
