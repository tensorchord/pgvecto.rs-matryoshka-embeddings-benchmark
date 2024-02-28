with open("results-adaptive.txt") as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    # print(lines)
    # Calculate the average accuracy for each limit.
    accuracy = {}
    for line in lines:
        line = line.split(",")
        print(line)
        if line[1] not in accuracy:
            accuracy[line[1]] = [float(line[2]), float(line[3])]
        else:
            accuracy[line[1]][0] += float(line[2])
            accuracy[line[1]][1] += float(line[3])
    for key in accuracy:
        accuracy[key][0] = accuracy[key][0] / (len(lines) / 5)
        accuracy[key][1] = accuracy[key][1] / (len(lines) / 5)
    print(accuracy)
