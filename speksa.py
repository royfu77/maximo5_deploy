#!/bin/env python
import sys
import mysql.connector


def load_file(filename):
    with open(filename, 'r') as log:
        f = []
        for line in log:
            if line != '\r\n':
                f.append(line.strip())
        return f


def parse_list(inputlist):
    count = 0
    output = {}
    bad_lines = {}
    unparsed = {}
    list_with_bad_value = []
    list_with_value = []
    rownum = 0
    errflag = {'DISPATCH': 0, 'LEVEL': 0, 'CLIENT': 0, 'SUBGROUP': 0, 'TIME': 0, 'SESSION': 0, 'ENTRY': 0}
    for row in inputlist:
        if row.startswith('DISPATCH'):
            count += 1
            if count != 1 and rownum - errflag['DISPATCH'] < 7:
                unparsed[rownum] = row.strip()
                errflag['DISPATCH'] = rownum
                rownum += 1
                continue
            errflag['DISPATCH'] = rownum
            list_with_bad_value = []
            list_with_value.append(row.strip().split('=')[1])
            list_with_bad_value.append(row.strip().split('=')[1])
        elif row.startswith('LEVEL'):
            if count != 1 and rownum - errflag['LEVEL'] < 7:
                unparsed[rownum] = row.strip()
                errflag['LEVEL'] = rownum
                rownum += 1
                continue
            errflag['LEVEL'] = rownum
            list_with_value.append(row.strip().split(':')[1])
        elif row.startswith('CLIENT'):
            if count != 1 and rownum - errflag['CLIENT'] < 7:
                unparsed[rownum] = row.strip()
                errflag['CLIENT'] = rownum
                rownum += 1
                continue
            errflag['CLIENT'] = rownum
            list_with_value.append(row.strip().split(':')[1])
        elif row.startswith('SUBGROUP'):
            if count != 1 and rownum - errflag['SUBGROUP'] < 7:
                unparsed[rownum] = row.strip()
                errflag['SUBGROUP'] = rownum
                rownum += 1
                continue
            errflag['SUBGROUP'] = rownum
            list_with_value.append(row.strip().split(':')[1])
        elif row.startswith('TIME'):
            if count != 1 and rownum - errflag['TIME'] < 7:
                unparsed[rownum] = row.strip()
                errflag['TIME'] = rownum
                rownum += 1
                continue
            errflag['TIME'] = rownum
            list_with_value.append(':'.join(row.strip().split(':')[1:]))
            list_with_bad_value.append(':'.join(row.strip().split(':')[1:]))
        elif row.startswith('SESSION'):
            if count != 1 and rownum - errflag['SESSION'] < 7:
                unparsed[rownum] = row.strip()
                errflag['SESSION'] = rownum
                rownum += 1
                continue
            errflag['SESSION'] = rownum
            list_with_value.append(row.strip().split(':')[1])
        elif row.startswith('ENTRY'):
            if count != 1 and rownum - errflag['ENTRY'] < 7:
                unparsed[rownum] = row.strip()
                errflag['ENTRY'] = rownum
                rownum += 1
                continue
            errflag['ENTRY'] = rownum
            list_with_value.append(':'.join(row.strip().split(':')[1:]))
            output[count] = list_with_value
            list_with_value = []
        else:
            list_with_bad_value.append(row)
            bad_lines[count] = list_with_bad_value
        rownum += 1

    return output, bad_lines, unparsed


def time_correction(date):
    from datetime import datetime
    result=datetime.strptime(date, '%m.%d.%Y %H:%M:%S').strftime("%Y-%m-%d %H:%M:%S")
    return result


def entry_correction(line):
    return line.replace("'", '"')


def insert_into_db(main_dict, error_dict, unparsed):
    conn = mysql.connector.connect(user = 'root',
                                   password = 'password',
                                   host = '10.0.0.1',
                                   database = 'speksa')
    cursor = conn.cursor()
    count = 0
    for key in main_dict.keys():
        count += 1
        query = "insert into speksa.log(dispatch, level, client, subgroup, time, session, entry) values" \
                "(%s, '%s', '%s', '%s', '%s', '%s', '%s');" % (main_dict[key][0], main_dict[key][1], main_dict[key][2], main_dict[key][3], time_correction(main_dict[key][4]), main_dict[key][5], entry_correction(main_dict[key][6]))
        cursor.execute(query)
        if count == 1000:
            conn.commit()
    conn.commit()
    count = 0
    for key in error_dict.keys():
        count += 1
        query = "insert into speksa.error(dispatch,time, message) values (%s, '%s', '%s')"\
                % (error_dict[key][0], time_correction(error_dict[key][1]), entry_correction(error_dict[key][2]))
        cursor.execute(query)
        # print query
        if count == 1000:
            conn.commit()
    conn.commit()
    count = 0
    for key in unparsed.keys():
        count += 1
        query = "insert into speksa.unparsed(message) values ('%s')" % (unparsed[key])
        cursor.execute(query)
        if count == 1000:
            conn.commit()
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main_dict, error_dict, unparsed_dict = parse_list(load_file(sys.argv[1]))
    print "Will be insert in log: "+str(len(main_dict))
    print "Will be insert in error: "+str(len(error_dict))
    print "Will be insert in unparsed: "+str(len(unparsed_dict))
    insert_into_db(main_dict, error_dict, unparsed_dict)
