#!/usr/bin/env python3

import sys

### There will be work hours and shift quantity determination.

month = input('Month number (from 1 to 12): ')
	
### 2021 working hrs ###

if int(month) == 1:
	work_hours_quantity = 120
elif int(month) == 2:
	work_hours_quantity = 151
elif int(month) == 3:
	work_hours_quantity = 176
elif int(month) == 4: 
	work_hours_quantity = 175
elif int(month) == 5:
	work_hours_quantity = 152
elif int(month) == 6:
	work_hours_quantity = 167
elif int(month) == 7:
	work_hours_quantity = 176
elif int(month) == 8:
	work_hours_quantity = 176
elif int(month) == 9:
	work_hours_quantity = 176
elif int(month) == 10:
	work_hours_quantity = 168
elif int(month) == 11:
	work_hours_quantity = 159
elif int(month) == 12:
	work_hours_quantity = 176
else:
	sys.exit('\n'+'Mistake in month num!!!' + '\n')
	
night_shifts = input('Full night shifts (w/o holiday hrs): ')
add_hours_night = input('Add night hrs, if needed (\"0\" if not): ')
holiday_hours = input('Holiday hrs: ')
night_hours = int(night_shifts) * 8 + int(add_hours_night)

### Vacation info
vacation = input('Vacation days w/o day-offs (5d/40hrs working week): ')
vacation_hours = int(vacation) * 8

### there will be hour/shift/bonus price determination

hour_price = round((81000 / work_hours_quantity), 2)
if vacation_hours != 0:
	day_price = (work_hours_quantity - night_hours - int(holiday_hours) - vacation_hours) * hour_price
else:
	day_price = (work_hours_quantity - night_hours - int(holiday_hours)) * hour_price

night_price = night_hours * hour_price * 1.6
holiday_price = (int(holiday_hours) * hour_price) * 2
result = round(((day_price + night_price + holiday_price) * 0.87), 2)

### bonus info

bonus_month = [1, 4, 7, 10]

### final result

print('#' * 40)
print('\n' + 'Salary is:')
print(result)
if int(month) in bonus_month:
	print('+ quorter bonus roughly 20000')
if vacation_hours != 0:
	#87 rubles eto primerno, t.k schitaut vidimo srednuu realnyu stoimost
	#chasa za poslednee vremya vmeste s nadbavkami
	vac = round(((vacation_hours * (hour_price + 168)) * 0.87), 2)
	print('+ there was vacation payment last month roughly {}'.format(vac) + '\n')
else:
	print('')


