template = '/html/body/div[2]/div/div/div[2]/div/div[1]/div/a'
schools = ["Бизнес-школа" , "ИШИнЭс" , "ИШИТР" , "ИШНКБ" , "ИШНПТ" , "ИШПР" , 
           "ИШЭ" , "ИЯТШ" , "ИШФВП" , "ИШХБМТ" , 'УН' , "УОД" , "ШОН"]

def findSchoolXPatch(school):
    for index in range(len(schools)):
        if schools[index].lower() == school.lower():
            return template + f'[{index + 1}]'
    