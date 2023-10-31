import base64
import datetime as dt
import numpy as np
import pandas as pd
import random
import uuid


def char_range(c1: chr, c2: chr) -> list[str]:
    """Return list of characters from between c1 and c2
    
    Args:
        c1 (char): The first character.
        c2 (char): The second character.
    """
    cList = []
    cMin = min(ord(c1), ord(c2))
    cMax = max(ord(c1), ord(c2))
    for c in range(cMin, cMax+1):
        cList.append(str(chr(c)))
    return cList

def quick_char_list(x: int) -> list[chr]:
    """Generate a list of X characters starting from A and not skipping any"""
    cList = []
    cEnd = chr(ord('A') + x - 1)
    return(char_range('A', cEnd))

def new_uuid() -> str:
    """Generate a unique ID and return as string"""
    r_uuid = str(base64.urlsafe_b64encode(uuid.uuid4().bytes))[2:-1]
    return r_uuid.replace('=', '')

def new_opening_duration(branchMod, dptMod):
    """Using the weights of the org branch and department, generate a duration for the role to be open around a normal distribution of a set mean and SD"""
    weight = 1 + (branchMod + dptMod)
    return(max(0, round(np.random.normal(MEAN_ROLL_FILL*weight, 7))))

def generate_branches(total: int):
    """Return list of lists, each leaf containing a character ID for the branch and a scaling float for "efficiency"
    
    Args:
        total (int): The number of branches.
    """
    chars = quick_char_list(total)
    branchList = []
    for i in range(len(chars)):
        branchList.append([chars[i], round(np.random.normal(0, BRANCH_EFFICIENCY_SD), 2)])
    return(branchList)

def generate_unfilled_opening(brn, dpt):
    """Return the data for a role that has been open for an amount of time typical for the org"""
    tempOpenID = new_uuid()    
    dur = new_opening_duration(brn[1], dpt[1])
    curDate = dt.datetime.today()
    postDate = curDate + dt.timedelta(days = -1 * dur)
    return([tempOpenID, dt_to_string(postDate), brn[0], dpt[0], 0, None, dur])

def generate_filled_opening(brn, dpt):
    """Return the data for a role that has been filled some time in the past, from 1 day ago to the max defined by the simulation years constant."""
    tempOpenID = new_uuid()    
    dur = new_opening_duration(brn[1], dpt[1])
    curDate = dt.datetime.today()
    daysAgo = dur + random.randint(1, RANGE_OF_DATA_YRS * 365)
    postDate = curDate + dt.timedelta(days = -1 * daysAgo)
    fillDate = postDate + dt.timedelta(days = dur)    
    return([tempOpenID, dt_to_string(postDate), brn[0], dpt[0], 1, dt_to_string(fillDate), dur])

def dt_to_string(dtIn):
    """Convert a datetime object to a YYYY-MM-DD string."""
    if dtIn is None:
        return None
    else:
        year = dtIn.strftime("%Y")
        month = dtIn.strftime("%m")
        day = dtIn.strftime("%d")
        return(year + "-" + month + "-" + day)
        
def generate_active_talent(inJob):
    """Return talent data for talent who are in the selection pipeline for a specific role, but not yet hired.
    Weighted random assignment to where the talent was sourced from and what stage they are in."""
    sourceChannel = ['Referral', 'Company Website', 'Job Board', 'Other']
    source = random.choices(sourceChannel, weights=(2,4,4,1), k = 1)

    selectionStages = ['Interview', 'KSAO Assessment', 'Onsite', 'Offer and Negotiation']    
    stage = random.choices(selectionStages, weights=(random.randint(60,80),random.randint(30,50),random.randint(10,20), random.randint(1,15)), k = 1)    
    return ([source[0], "active", inJob[0], stage[0], inJob[1]])

def generate_current_employee(inJob):
    """Return talent data for talent who are employeed at org within the specified role.
    Weighted random assignment to where the talent was sourced from"""
    sourceChannel = ['Referral', 'Company Website', 'Job Board', 'Other']
    source = random.choices(sourceChannel, weights=(random.randint(6,8),random.randint(4,6),random.randint(1,4),random.randint(1,2)), k = 1)
    return ([source[0], "hired", inJob[0], None, inJob[1]])
    
def generate_rejected_talent(inJob):
    """Return talent data for talent who were rejected.
    Weighted random assignment to where the talent was sourced from and what stage they were rejected at."""
    sourceChannel = ['Referral', 'Company Website', 'Job Board', 'Other']
    source = random.choices(sourceChannel, weights=(2,4,4,1), k = 1)

    selectionStages = ['Resume Screening', 'Interview', 'KSAO Assessment', 'Onsite', 'Offer and Negotiation']    
    stage = random.choices(selectionStages, weights=(random.randint(50,80),random.randint(35,70),random.randint(15,30),random.randint(7,15),random.randint(1,3)), k = 1)    
    return ([source[0], "rejected", inJob[0], stage[0], inJob[1]])

def generate_expense_jobBoard(inJob):
    """Return expense data for the specified role."""
    return ([inJob[0], "Job board listing", 200, inJob[1]])

def generate_expense_assessment(inJob):
    """Return expense data for the specified role."""
    return ([inJob[0], "Personnel assessment", 50, inJob[1]])

def generate_expense_onsite_travel(inJob):
    """Return expense data for the specified role."""
    return ([inJob[0], "Onsite travel", random.randint(30,500), inJob[1]])

def generate_expense_referral(inJob):
    """Return expense data for the specified role."""
    return ([inJob[0], "Internal referral bonus", 500, inJob[1]])


#Constants
FILLED_JOBS_PER_DEPARTMENT  = 200
RANGE_OF_DATA_YRS           = 1
BRANCH_EFFICIENCY_SD        = .3
MEAN_ROLL_FILL              = 28
SD_ROLL_FILL                = 7
BRANCHES                    = generate_branches(10)
DEPARTMENTS                 = [['Human Resources', 0.2],
                               ['Finance and Accounting', 0],
                               ['Marketing', 0.15],
                               ['Sales', 0.1],
                               ['Information Technology',-0.1],
                               ['Customer Service and Support', -0.3]]

#Lists to populate
openings    = []
talent      = []
expenses    = []


#Simulation
#Loop through each branch and randomly determine how many open positions there are.
#Then randomly choose a department within the branch and generate data, including random number of applicants.
for brn in BRANCHES:

    #Determine number of currently open positions in the branch
    ctCurOpen = max(0, random.randint(0,10) - 3)
    for i in range(0,ctCurOpen):
        dpt = DEPARTMENTS[random.randint(0,len(DEPARTMENTS) - 1)]
        tempOpening = generate_unfilled_opening(brn, dpt)
        expenses.append(generate_expense_jobBoard(tempOpening))
        openings.append(tempOpening)

        #generate active employees currently in the selection pipeline for the role and related expenses
        for i in range(0, random.randint(0,50)):
            tempTalent = generate_active_talent(tempOpening)
            if tempTalent[3] == 'KSAO Assessment':
                expenses.append(generate_expense_assessment(tempOpening))
            elif tempTalent[3] == 'Onsite':
                expenses.append(generate_expense_assessment(tempOpening))
                expenses.append(generate_expense_onsite_travel(tempOpening))
            talent.append(tempTalent)

    #Generate historical data for roles that have been filled, based on defined constant
    for i in range(0,FILLED_JOBS_PER_DEPARTMENT):
        dpt = DEPARTMENTS[random.randint(0,len(DEPARTMENTS) - 1)]
        filledJob = generate_filled_opening(brn,dpt)
        openings.append(filledJob)
        expenses.append(generate_expense_jobBoard(filledJob))
        expenses.append(generate_expense_assessment(filledJob))
        tempEmployee = generate_current_employee(filledJob)
        talent.append(tempEmployee)
        if tempEmployee[0] == "Referral":
            expenses.append(generate_expense_referral(filledJob))

        #generate employees who didn't get selected
        for i in range(0, random.randint(10,30)):
            tempTalent = generate_rejected_talent(filledJob)
            if tempTalent[3] == 'KSAO Assessment':
                expenses.append(generate_expense_assessment(filledJob))
            elif tempTalent[3] == 'Onsite' or tempTalent[3] == 'Offer and Negotiation':
                expenses.append(generate_expense_assessment(filledJob))
                expenses.append(generate_expense_onsite_travel(filledJob))
                
            talent.append(tempTalent)


#Convert lists to dataframe, sort, and clean final DF
openingsDF = pd.DataFrame(openings, columns = ['open_id',
                                               'post_date',
                                               'branch',
                                               'department',
                                               'filled',
                                               'fill_date',
                                               'duration'])
openingsDF.sort_values(['post_date', 'branch', 'department', 'open_id'], inplace=True)       

expenseID = range(1,len(expenses)+1)
expensesDF = pd.DataFrame(expenses, columns = ['role_id',
                                               'category',
                                               'amount',
                                               'sortDate'])
expensesDF.sort_values(['sortDate', 'role_id', 'category', 'amount'], inplace=True)   
expensesDF['expense_id'] = expenseID
expensesDF = expensesDF[['expense_id', 'role_id', 'category', 'amount']]

talentID = range(1,len(talent)+1)
talentDF = pd.DataFrame(talent, columns = ['source_channel',
                                           'status',
                                           'role_id',
                                           'rejected_after',
                                           'sortDate'])
talentDF.sort_values(['sortDate', 'status', 'source_channel', 'rejected_after'], inplace=True)   
talentDF['talent_id'] = talentID
talentDF = talentDF[['talent_id', 'source_channel', 'status', 'role_id', 'rejected_after']]

#Save all DF to .csv     
openingsDF.to_csv('generatedData\\openings.csv', index=False)
expensesDF.to_csv('generatedData\\expenses.csv', index=False)
talentDF.to_csv('generatedData\\talent.csv', index=False)

