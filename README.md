# FerherTbl
Infinity.FerherTbl

It started as a means to simplify my workload. That was to count inventory at Fehrer Automotive in Duncan, SC. Fehrer Automotive had an inventory issue where the warehouse staff were not properly picking the inventory, and allowing workers to come and grab what they needed for the assembly line without picking it out of the bins. I was hired as a temp through Prologistix in Duncan, SC to help as a cycle counter. At the time there was a team of 4 including the lead. A 1st shift and a 2nd shift.

On day 1 I was given a piece of notepad paper and was instructed to walk up and down each aisle of racking. These isles were like 20 feet or so. Most of the products consist of plastic wrapped pallets of boxes or parts with a piece of paper that had a list of item numbers and counts listed on them. Our job was to list and count everything. At the end of the shift I had 2 sheets front and back full items numbers and counts.

When we reported to the manager, we were all asked to add up all of our counts. I froze thinking…it’s 20 minutes until the end of our shift…I proceeded to go down the list and pulled out my phone’s calculator. Going down the list I’m thinking, this isn’t going to happen. This is going to take like 2 hours. So I went to the manager and said as such. He took all of our papers and sent us off.

The next day I tried again, attempting to group together product numbers. Again, at the end of my shift we stopped early to calculate our totals, and while looking for patterns I started to organize the numbers by their prefixes and suffixes by organizing them into tables. I would write a template titled with the prefix, a place to put the counter’s name and date. I then made 10 copies of each for our team to use.

I used to write numbers in the cells provided and add up the counts at the end of each shift. I kept running into 2 problems though. A) I always ran out of space in the space of each suffix cell. And B) I would regularly have to rewrite a new table every time a new suffix was encountered. For the first problem I would start tallying, but for the 2nd problem I wrote a python script that would generate an html page for each prefix containing a grid of cells for each suffix and a space for counts…convert to pdf then print 10 copies of each once per week. After some time I found that simply tallying isn’t working either so I thought…instead of writing vertical lines and a diagonal to indicate 5, use dots. Same idea as tallies but we use up to 4 dots, then draw a line through the dots to indicate 5.

This process alone saved us HOURS of work. Physically counting the stock was fast and summing the totals for each product too. Whereas before, counting would take most of the shift and totaling took the last 1 or 2 hours.

One day, I was sitting with a calculator doing my counts and thought, what if I used a number pad, and entered the counts into a program that would track the counts? It would be no different than using a calculator, except that we wouldn’t need to write the totals. So I started working on a text-based prompt in python. I wrote a script that showed a list of prefixes with the one in focus being highlighted, below a list of suffixes, with again the one active being highlighted, and a prompt.

You could enter your counts in a number of ways. (count)x(multiplier) separated by commas. The multiplier was optional. Then when you're done with the counts for that suffix you could type ++, then enter to advance to the next suffix. I added logic remove counts, to goto the previous suffix, goto a specific suffix, and prefix as well. Suffixes that have not been encountered before are automatically added and get appended to the suffix list for the table generation function. The functionality was not complete and had some bugs, and since I didn’t have much demand to crack them out I pushed it off.

Our lead at the time got caught up in some controversy and got suspended pending review, in the meantime I became acting lead, and at the end of the next shift I was responsible for taking everyone's counts and entering them into an excel spreadsheet. After half an hour in
I realized that I REALLY need to fix the bugs so I can do this efficiently. So after I went home I spent the weekend fixing the problems and getting the script hosted on my google cloud compute instance. At the end of each shift I would enter counts and work out bugs as they occurred. When I was done, I would export an excel spreadsheet containing the item numbers and their counts. Print them off and slide them under the logistics coordinator’s office door before leaving for the night.

After some time I was sending the counts via email, also as per request of the logistics coordinator, I organized the spreadsheets into different sheets. One for the day’s counts, indicating item number, description, bin location(s), Per Box Quantity, number of boxes, number of partials, and a total. Another sheet for the same data excluding bin locations. A 5 day coverage of counts, also indicating when the item was last seen. And finally, a sheet covering inventory that is running low.


Next, we needed accountability for incorrect data being supplied as a result of negligence. So I implemented multi user functionality. When I created a new user I would prompt them for a username and a pin would be generated. They would use their phone to login in, update the pin, and supply their phone number and email address for contact purposes. Each user had the ability to enter their own counts and submit them. I trained them how to enter the counts properly and how to navigate prefixes/suffixes. Each of us would divide the prefix tables up so that we didn’t have multiple people working on the same counts. After our counts they would disperse and enter them into the system. Now that they entered their own counts it took all of us around 10-20 minutes to enter our data and a spreadsheet was generated. If something came up, we could see exactly who was responsible for what counts.

At one point there was a need to view a count for a specific bin or an item, so I wrote a prompt  that would read the count data. If you entered a bin, it would show a report of what items were in that bin, their counts, and for each date submitted. Similarly, if you entered an item number, you would see a list of bins and the count of the item in each bin. For each date as well. There were many times that the warehouse staff made use of this to find what they needed to pick and pull.

One day a few suits from Germany showed up to help clean up the inventory issue. One day they shut down production and everybody…and I mean everybody was given a notepad and paper and told to write counts for a given section. They all sat down, totaled their counts, and put those counts on pink sheets. The higher ups took all of the data and generated a report of active inventory. I entered my counts into my system and printed off a report in minutes.

They refused to use my system that had been working reliably for months. Which was ok.

However, to wrap up…attendance ended up being my downfall. As a temp…you're a temp. Policy is policy, and a contract is a contract. No back solicitation clauses. Found out months after I was gone by running into someone that I trained said they went back to pen and paper and how badly they wanted the system back.

Since this project, I’ve had a strong drive to engineer a solution like this one again in the future. One that will thrive and make our lives just a little easier…or a lot easier and at the same time not take all of the work out of the job.