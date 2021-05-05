#!/usr/bin/env python
import sys
import subprocess
import time
import calendar

USER="REPLACE THIS WITH YOUR GERRIT ID"

def commits_by_company(period_name, start_date, end_date):
   #set gerrit ssh connection parameters to allow for timeouts
   interval = 2
   retries = 3

   # Get Projects
   projects = subprocess.check_output("ssh -p 29418 " +USER \
                                      +" gerrit ls-projects", shell=True)
   project_list = projects.strip().split("\n")

   # Get Developers by Company (CI group)
   companies = subprocess.check_output("ssh -p 29418 " +USER \
                                       +" gerrit ls-groups", shell=True)
   companies = companies.strip().split("\n")
   company_list = []

   for company in companies:
      if company:
         if "Administrators" in company:
            continue
         if "openbmc" in company:
            continue
         if "owners" not in company:
            company_list.append(company.split('/')[0])

            devs = subprocess.check_output("ssh -p 29418 " +USER \
                                           +" gerrit ls-members " \
                                           +company \
                                           ,shell=True)
            devs = devs.strip().split("\n")
            company_total = 0

            for dev in devs:
               if dev:
                  if "username" in dev:
                     continue
               commit_total = 0
               dev_id = dev.split()[0]
               dev_name = dev.split()[1]

               #filtering autobumps and openbmc/openbmc project commits (mostly bumps)
               # *** future enhancement - make commit_arg optionally passed in
               for project in project_list:
                  if project == "openbmc/openbmc":
                     continue
                  commit_arg = "ssh -p 29418 " +USER \
                               + " gerrit query --format=JSON status:merged \
                               AND after:" +start_date \
                               +" AND before:" +end_date \
                               +" AND NOT topic:autobump \
                               AND owner:" +dev_id \
                               +" AND project:" +project \
                               +" | grep rowCount"
                  for x in range(retries):
                     try:
                        commits = subprocess.check_output(commit_arg, shell=True)
                        break
                     except Exception, e:
                        time.sleep(interval)
                  if commits:
                     commit_count = commits.split("rowCount\":")[1].split(",")[0]
                     if commit_count != "0":
                     #print("," +project +"," +commit_count)
                        commit_total += int(commit_count)
               print(dev_id +" " +dev_name +"," +str(commit_total))
               company_total += commit_total
            print(company.split('/')[0])
            print(period_name +", " +str(company_total))
            print("")


def do_month():
   if len(sys.argv) > 1 :
      year = sys.argv[1]
      month = sys.argv[2]
   else:
      print
      print("Usage: merges_by_company <Year YYYY> <Month MM>  > <Outputfile> ")
      print
      return

   if (int(month) > 0) and (int(month) < 13):
      commits_by_company(calendar.month_name[int(month)], year +"-" + month
                         + "-01", year +"-" + month + "-"
                         + str(calendar.monthrange(int(year), int(month))[1]))
   else:
      print
      print("Check Usage: Month must be a number between 1 and 12")
      print
      
def main():
   do_month()


if __name__== "__main__":
  main()
