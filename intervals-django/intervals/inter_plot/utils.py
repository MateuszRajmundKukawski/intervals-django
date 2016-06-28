# -*- coding: utf-8

import matplotlib
matplotlib.use('Agg')
import os
from datetime import datetime
from LatLon import LatLon, Latitude, Longitude
import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom



# zakresyTetna = [40, 126, 138, 152, 163, 177, 190]
ZAKRESY_TETNA_KOLORY = {'0': 'grey',
                      '1': 'lightgreen',
                      '2': 'darkgreen',
                      '3': 'yellow',
                      '4': 'orange',
                      '5': 'red',
                      }


def obliczZakresyTetna(wiek, zakresyTetnaProcenty):
    zakresyTetna = []

    # jak chesz float w wyniku to wystarczy dodać .
    tetnoMax = 220. - wiek
    tetnoMin = 40
    zakresyTetna.append(tetnoMin)
    for zakres in zakresyTetnaProcenty:
        tetnoTemp = int(zakres / 100. * tetnoMax)
        zakresyTetna.append(tetnoTemp)
    return zakresyTetna


def parse_training(fileName, dt=True):
    listaPkt = []
    tetno = 0
    DOMTree = minidom.parse(fileName)
    cNodes = DOMTree.childNodes
    # timeParsed = parseTime(cNodes[0].getElementsByTagName("time")[1].childNodes[0].toxml())
    # czas = cNodes[0].getElementsByTagName("time")[1].childNodes[0].toxml().split('T')
    # czas1 = czas[0] + ':' + czas[1].strip('Z')
    # czas2 = datetime.strptime(czas1, '%Y-%m-%d:%H:%M:%S')
    # czasPoprz = czas2
    for dane in cNodes[0].getElementsByTagName("trkpt"):
        element = []
        Lat = dane.getAttribute("lat")
        Lon = dane.getAttribute("lon")
        # print('Lat = %s' % Lat
        # print('Lon = %s' % Lon
        # timeParsed = parseTime(cNodes[0].getElementsByTagName("time")[0].childNodes[0].toxml().split('T'))
        czas = dane.getElementsByTagName("time")[0].childNodes[0].toxml().split('T')
        try:
            tetno = dane.getElementsByTagName("gpxtpx:hr")[0].childNodes[0].toxml()
        except Exception as err:
            pass
        czas1 = czas[0] + ':' + czas[1].strip('Z')
        czas2 = datetime.strptime(czas1, '%Y-%m-%d:%H:%M:%S')
        # timeDiff = czas2 - czasPoprz
        # print('Time = %s' % timeDiff
        if dt:
            element = [Lat, Lon, czas2, float(tetno)]
        else:
            element = [Lat, Lon, str(czas2), float(tetno)]

        listaPkt.append(element)
    return listaPkt


def szukajInterwalow(wykresTableY, ccuracy_liczba_probek, accuracy_pace_diff_for_interval_search, point_distance_minimal_between_interwals):
    startInterwalu = []
    stopInterwalu = []
    startFound = 0
    for i, tempo in enumerate(wykresTableY):
        if i > ccuracy_liczba_probek:
            if startFound == 0:
                licznik = 0
                for j in range(1, ccuracy_liczba_probek):  # szuka startu interwalu
                    paceTemp = wykresTableY[i] - wykresTableY[i - j]
                    if paceTemp < -accuracy_pace_diff_for_interval_search:
                        licznik += 1
                    else:
                        break
                    paceTemp = 0
                if licznik == (
                    ccuracy_liczba_probek - 1):  # sprawdza czy kolejnych 'ccuracy_liczba_probek' probek ma tempo o 'accuracy_pace_diff_for_interval_search' wieksze od probki bazowej
                    if len(startInterwalu) != 0:
                        if (i - startInterwalu[len(
                                startInterwalu) - 1]) > point_distance_minimal_between_interwals:  # sprawdza czy nie znalazl kolejnego punktu bezposrednio obok poprzedniego
                            startInterwalu.append(i)
                            startFound = 1  # flaga- mozna zaczac szukanie konca interwalu
                    else:
                        startInterwalu.append(i)
                        startFound = 1  # flaga- mozna zaczac szukanie konca interwalu
            if startFound == 1:
                licznik = 0
                for j in range(1, ccuracy_liczba_probek):  # szuka stopu interwalu
                    paceTemp = wykresTableY[i] - wykresTableY[i - j]
                    if paceTemp > accuracy_pace_diff_for_interval_search:
                        licznik += 1
                    else:
                        break
                    paceTemp = 0
                if licznik == (
                    ccuracy_liczba_probek - 1):  # sprawdza czy kolejnych 'ccuracy_liczba_probek' probek ma tempo o 'accuracy_pace_diff_for_interval_search' mniejsze od probki bazowej
                    if len(stopInterwalu) != 0:
                        if (i - stopInterwalu[len(
                                stopInterwalu) - 1]) > point_distance_minimal_between_interwals:  # sprawdza czy nie znalazl kolejnego punktu bezposrednio obok poprzedniego
                            stopInterwalu.append(i)
                            startFound = 0
                    else:
                        stopInterwalu.append(i)
                        startFound = 0
            else:
                continue
    return startInterwalu, stopInterwalu


def obliczPolozenie(listaWspol):
    wykresTableX = []
    wykresTableY = []
    czasy = []
    tetno = []
    totalDistance = 0
    prevCzas = listaWspol[1][2]
    for i, punkt in enumerate(listaWspol):
        if i > 0:
            punkt1 = LatLon(listaWspol[i - 1][0], listaWspol[i - 1][1])
            punkt2 = LatLon(Latitude(listaWspol[i][0]), Longitude(listaWspol[i][1]))
            distance = punkt1.distance(punkt2)
            if distance != 0:
                czasDiff = listaWspol[i][2] - prevCzas
                prevCzas = listaWspol[i][2]
                totalDistance += distance
                try:
                    pace = (czasDiff.total_seconds() / 60) / distance
                except Exception as err:
                    pass
                if pace < 20:
                    elementDoPrintu = [totalDistance, pace]
                    wykresTableX.append(totalDistance)
                    wykresTableY.append(pace)
                    czasy.append(listaWspol[i][2])
                    tetno.append(listaWspol[i][3])
    return wykresTableX, wykresTableY, totalDistance, czasy, tetno


def plotPace(wykresTableX, wykresTableY, paceAverageTable, tetno, file_name, zakresyTetna):
    plot_title = os.path.basename(file_name)
    if sum(tetno) / len(
            tetno):  # sprawdza czy wartosci tetna nie sa zerami(zera sa wpisywane, jezeli w .gpx nie ma tagow hr)
        fig, ax = plt.subplots(figsize=(15, 9))
        plt.subplot(212)
        # fig, ax = plt.subplots()
        plt.plot(wykresTableX, tetno, linewidth=4, color='brown')
        plt.axis([0, max(wykresTableX), zakresyTetna[0], zakresyTetna[6]])
        plt.xlabel('Distance')
        plt.ylabel('Pulse')
        plt.title('Pulse zones')
        x = np.asarray(wykresTableX)
        y = np.asarray(tetno)
        tetnoZakres = []
        for tetnoEl in tetno:
            if tetnoEl >= zakresyTetna[0] and tetnoEl < zakresyTetna[1]:
                tetnoZakres.append(0)
            elif tetnoEl >= zakresyTetna[1] and tetnoEl < zakresyTetna[2]:
                tetnoZakres.append(1)
            elif tetnoEl >= zakresyTetna[2] and tetnoEl < zakresyTetna[3]:
                tetnoZakres.append(2)
            elif tetnoEl >= zakresyTetna[3] and tetnoEl < zakresyTetna[4]:
                tetnoZakres.append(3)
            elif tetnoEl >= zakresyTetna[4] and tetnoEl < zakresyTetna[5]:
                tetnoZakres.append(4)
            elif tetnoEl >= zakresyTetna[5] and tetnoEl < zakresyTetna[6]:
                tetnoZakres.append(5)
            else:
                tetnoZakres.append(-1)
        y1 = np.asarray(tetnoZakres)
        for i in range(0, 6):
            labelTemp = str(zakresyTetna[i]) + ':' + str(zakresyTetna[i + 1])
            plt.fill_between(x, y, where=y1 == i, facecolor=ZAKRESY_TETNA_KOLORY[str(i)], alpha=1, interpolate=True)
            plt.axhline(zakresyTetna[i], color=ZAKRESY_TETNA_KOLORY[str(i)], lw=5, alpha=0.8, label=labelTemp)
        plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
        tetnoZakresDict = dict([(x, tetnoZakres.count(x)) for x in tetnoZakres])
        for x in tetnoZakresDict:
            tetnoZakresDict[x] = 100 * float(tetnoZakresDict[x]) / float(
                len(tetnoZakres))  # procentowy udzial kazdego zakresu

        plt.subplot(211)
    plt.plot(wykresTableX, wykresTableY)
    plt.axis([0, max(wykresTableX), 0, 20])
    plt.gca().invert_yaxis()
    for anot in paceAverageTable:
        anotXStart = anot[0]
        anotXStop = anot[1]
        anotY = anot[2]
        anotText = anot[3]
        startPoint = anot[4]
        stopPoint = anot[5]
        dist = anotXStop - anotXStart
        xTemp = wykresTableX[startPoint:stopPoint]  # lista wartosci X dla interwalu, do wyrysowania prostej linii
        yTemp = []
        for i in range(0, len(xTemp)):
            yTemp.append(anotY)  # wypelnienie wartosci Y srednim tempem obliczonym dla interwalu
        plt.plot(xTemp, yTemp, linewidth=2, color='red')
        plt.annotate('Pace: %s' % anotText, xy=(anotXStart, anotY), xytext=(anotXStart, anotY - 2))
        # arrowprops=dict(facecolor = 'black', shrink = 0.05),
        # )
        plt.annotate(' D: %.2fkm' % dist, xy=(anotXStop, anotY), xytext=(anotXStart, anotY - 3),
                     )
    plt.xlabel('Distance')
    plt.ylabel('Pace')
    plt.title(plot_title)
    if sum(tetno) / len(tetno):
        return tetnoZakresDict
        # plt.figure(figsize=(10.0, 9.0))
        # plt.show()


def averagingFilter(wykresTableY, filter_order):
    wykresTableYAverage = []
    for i, tempo in enumerate(wykresTableY):
        if i > int(filter_order / 2) and i < int(len(wykresTableY) - int(filter_order / 2)):
            suma = 0
            for j in range(int((-1) * (filter_order / 2)), int(filter_order / 2 + 1)):
                suma += wykresTableY[i + j]
            elAver = suma / filter_order
            wykresTableYAverage.append(elAver)
    return wykresTableYAverage


def get_data(
        output_dir,
        fileName,
        ccuracy_liczba_probek,
        accuracy_pace_diff_for_interval_search,
        point_distance_minimal_between_interwals,
        filter_order,
        wiek,
        zakresyTetnaProcenty
):
    # wiek
    print_list = []
    # fileName = sys.argv[1]
    # accuracy_pace_diff_for_interval_search = sys.argv[2]
    # ccuracy_liczba_probek = sys.argv[3]
    zakresyTetna = obliczZakresyTetna(wiek, zakresyTetnaProcenty)
    listaWspol = parse_training(fileName)
    wykresTableX, wykresTableY, totalDistance, czasy, tetno = obliczPolozenie(listaWspol)
    wykresTableYAverage = averagingFilter(wykresTableY, filter_order)
    startInterwalu, stopInterwalu = szukajInterwalow(wykresTableYAverage, ccuracy_liczba_probek, accuracy_pace_diff_for_interval_search, point_distance_minimal_between_interwals)
    paceAverageTable = []
    print_list.append('\n_-_-_-_-_- INTERVALS _-_-_-_-_-')
    print(print_list[-1])  #'\n_-_-_-_-_- INTERVALS _-_-_-_-_-'
    for i in range(0, len(startInterwalu)):
        element = []
        distanceStart = wykresTableX[startInterwalu[i] + int(filter_order / 2) + 2]
        distanceStop = wykresTableX[stopInterwalu[i] - int(filter_order / 2)]
        czasStart = czasy[startInterwalu[i] + int(filter_order / 2) + 2]
        czasStop = czasy[stopInterwalu[i] - int(filter_order / 2)]
        czasDiffPaceAverage = czasStop - czasStart
        paceAverage = (czasDiffPaceAverage.total_seconds() / 60) / (distanceStop - distanceStart)
        paceTempStr = int((paceAverage - int(paceAverage)) * 60)
        if paceTempStr < 10:
            paceAverageString = str(int(paceAverage)) + ':0' + str(paceTempStr)
        else:
            paceAverageString = str(int(paceAverage)) + ':' + str(paceTempStr)
        element = [distanceStart, distanceStop, paceAverage, paceAverageString,
                   startInterwalu[i] + int(filter_order / 2) + 2, stopInterwalu[i] + int(filter_order / 2)]
        paceAverageTable.append(element)
        print_list.append('\n')
        print(print_list[-1])  #'\n'
        print_list.append('Point number:\t %s' % int(startInterwalu[i] + int(filter_order / 2)))
        print(print_list[-1])  #'Point number:\t %s' % int(startInterwalu[i] + int(filter_order / 2))
        print_list.append('Distance start:\t %.2f' % distanceStart)
        print(print_list[-1])  #'Distance start:\t %.2f' % distanceStart
        print_list.append('Distance stop:\t %.2f' % distanceStop)
        print(print_list[-1])  #'Distance stop:\t %.2f' % distanceStop
        print_list.append('Distance:\t %.2f' % (distanceStop - distanceStart))
        print(print_list[-1])  #'Distance:\t %.2f' % (distanceStop - distanceStart)
        print_list.append('Pace average:\t %s' % paceAverageString)
        print(print_list[-1])  #'Pace average:\t %s' % paceAverageString
        print_list.append('\n_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-')
        print(print_list[-1])  #'\n_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-'
    print_list.append('\nTotal distance:\t %.2f\n' % totalDistance)
    print(print_list[-1])  #'\nTotal distance:\t %.2f\n' % totalDistance
    # print(print_list[-1]  #len(startInterwalu)

    tetnoZakresDict = plotPace(wykresTableX, wykresTableY, paceAverageTable, tetno, fileName, zakresyTetna)
    if tetnoZakresDict is not None:
        print_list.append('_-_-_-_-_- PULSE ZONES _-_-_-_-_-\n')
        print(print_list[-1])  #'_-_-_-_-_- PULSE ZONES _-_-_-_-_-\n'
        for i, x in enumerate(tetnoZakresDict):
            tempText = 'Zakres' + str(i) + ': ' + str(int(tetnoZakresDict[x])) + ' %'
            print(print_list[-1])  #tempText
            print_list.append(tempText)
            # print(print_list[-1]  #'Zakres%i: %.1f\x25' % (x, tetnoZakresDict[x])
        print_list.append('\n_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-')
        print(print_list[-1])  #'\n_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-'

    # plt.plot(wykresTableYAvrage)
    # plt.gca().invert_yaxis()
    base_name = os.path.basename(fileName)[:-3] + 'png'
    out_path = os.path.join(output_dir, base_name)
    plt.savefig(out_path)
    return base_name, print_list
##############################
# my utils
##############################


def datetime_js_to_date(js_date):
    return datetime.strptime(js_date, '%M/%d/%Y')


if __name__ == '__main__':
    fileName = "/home/mati/Pulpit/xxx.gpx"
    CCURACY_LICZBA_PROBEK = 8  # ile kolejnych probek ma byc wieksze (dla szukania startu) badz mniejsze (dla stopu) od probki aktualnie iterowanej
    accuracyPaceDiffForIntervalSearch = 1  # jakiej roznicy tempa (min / km) ma szukac
    point_distance_minimal_between_interwalsS = 10  # dla ilu kolejnych punktow olewac start / stop interwalu (jezeli jest 'dlugi rozped')
    filter_orderS = 5  # liczba probek do usrednienia, dla latwiejszego wykrywania startu / stopu
    # usredniam dane z x probek, przebieg robi sie mniej poszarpany, na wykresie sa wartosci oryginalne
    wiekS = 30
    zakresyTetnaProcentyS = [54, 63, 73, 81, 91, 100]

    get_data(".", fileName, CCURACY_LICZBA_PROBEK, accuracyPaceDiffForIntervalSearch, point_distance_minimal_between_interwalsS, filter_orderS, wiekS, zakresyTetnaProcentyS)
