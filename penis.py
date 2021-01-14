if __name__ == '__main__':
    print("--------")
    txt = "penis"
    print("--------"+txt)
    listt = list(txt)
    print("--------" + str(listt))

    listt += txt
    print("--------" + str(listt))
    listt[6] = "fe"
    print("--------" + str(listt))

    listt = txt
    print("--------" + str(listt))
    listt += txt
    print("--------" + str(listt))

    listt = [txt]
    print("--------" + str(listt))
    listt += txt
    print("--------" + str(listt))

    listt = [txt]
    print("--------" + str(listt))
    listt.append(txt)
    print("--------" + str(listt))