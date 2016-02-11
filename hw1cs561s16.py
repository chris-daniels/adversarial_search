import sys,os,copy

#given a certain board setup, return the value of that board
def getBoardValue(player, boardVals, boardOccupants):
	total = 0
	for i in range(0,len(boardOccupants)):
		for j in range(0,len(boardOccupants[i])):
			#print "comparing ", player, " with ", boardOccupants[i][j]
			if boardOccupants[i][j] == player:
				total += int(boardVals[i][j])
			if boardOccupants[i][j] != player and boardOccupants[i][j] != '*':
				total -= int(boardVals[i][j])
	return total

#returns opponent for a given character
def getOpponent(player):
	if(player == 'X'):
		return 'O'
	else:
		return 'X'

#print the state of the board to the next_state.txt file
def printNextState(boardOccupants,outputFile):
	for i in range(0,len(boardOccupants)):
		for j in range(0,len(boardOccupants[i])):
			outputFile.write(boardOccupants[i][j])
		outputFile.write('\n')

#log for minimax node visitation
def log(row,col,depth,value):
	with open('traverse_log.txt','a') as outputFile:
		if(depth == 0):
			outputFile.write('root')
		else:
			outputFile.write(chr(col + ord('A')))
			outputFile.write(str(row+1))
		outputFile.write(',')
		outputFile.write(str(depth))
		outputFile.write(',')
		if value == -sys.maxint-1:
			outputFile.write('-Infinity')
		elif value == sys.maxint:
			outputFile.write('Infinity')
		else:	
			outputFile.write(str(value))
		outputFile.write('\n')
		outputFile.close()

#log for alphabeta node visitation
def logab(row,col,depth,value,alpha,beta):
	with open('traverse_log.txt','a') as outputFile:
		if(depth == 0):
			outputFile.write('root')
		else:
			outputFile.write(chr(col + ord('A')))
			outputFile.write(str(row+1))
		outputFile.write(',')
		outputFile.write(str(depth))
		outputFile.write(',')
		if value == -sys.maxint-1:
			outputFile.write('-Infinity')
		elif value == sys.maxint:
			outputFile.write('Infinity')
		else:	
			outputFile.write(str(value))
		outputFile.write(',')
		if alpha == -sys.maxint-1:
			outputFile.write('-Infinity')
		else:
			outputFile.write(str(alpha))
		outputFile.write(',')
		if beta == sys.maxint:
			outputFile.write('Infinity')
		else:
			outputFile.write(str(beta))
		outputFile.write('\n')
		outputFile.close()

#removes last newline character when necessary
def removeLastChar(outputFile):
	outputFile.flush()
	if os.path.getsize(outputFile.name) != 0:
		outputFile.seek(-1, os.SEEK_END)
		outputFile.truncate()

#checks if a given move is a valid raid
def isValidRaid(row, col, player, boardOccupants):
	if boardOccupants[row][col] != '*': 
		return False
	if row > 0 and boardOccupants[row - 1][col] == player:
		return True
	if row < len(boardOccupants[0]) - 1 and boardOccupants[row + 1][col] == player:
		return True
	if col > 0 and boardOccupants[row][col - 1] == player:
		return True
	if col < len(boardOccupants) - 1 and boardOccupants[row ][col + 1] == player:
		return True
	return False

#checks if a given move is a valid sneak
def isEmpty(row, col, boardOccupants):
	if(boardOccupants[row][col] == '*'):
		return True
	else:
		return False

#performs a raid move and returns the board state
def raid(row, col, player, boardOccupants):
	boardOccupants[row][col] = player
	if row > 0 and boardOccupants[row - 1][col] != player and boardOccupants[row - 1][col] != '*':
		boardOccupants[row - 1][col] = player
	if row < len(boardOccupants[0]) - 1 and boardOccupants[row + 1][col] != player and boardOccupants[row + 1][col] != '*':
		boardOccupants[row + 1][col] = player
	if col > 0 and boardOccupants[row][col - 1] != player and boardOccupants[row][col - 1] != '*':
		boardOccupants[row][col - 1] = player
	if col < len(boardOccupants) - 1 and boardOccupants[row ][col + 1] != player and boardOccupants[row ][col + 1] != '*':
		boardOccupants[row ][col + 1] = player

#performs a sneak move and returns the board state
def sneak(row, col, player, boardOccupants):
	boardOccupants[row][col] = player

#greedy best first search algorithm
def greedyBestFirst(player, boardVals, boardOccupants,outputFile):
	#bestRow and bestCol will track the best move available
	bestRow = -1
	bestCol = -1
	#bestValue will track the best board value we have found
	bestValue = getBoardValue(player,boardVals,boardOccupants)
	#loop through every board location, determine value of that move
	for i in range(0,len(boardOccupants)):
		for j in range(0,len(boardOccupants[i])):
			#try raid
			if isValidRaid(i,j,player,boardOccupants):
				tempBoard = copy.deepcopy(boardOccupants)
				raid(i,j,player,tempBoard)
				tempValue = getBoardValue(player,boardVals,tempBoard)
				if tempValue > bestValue:
					bestRow = i
					bestCol = j
					bestValue = tempValue
			#try sneak
			elif isEmpty(i,j,boardOccupants):
				tempBoard = copy.deepcopy(boardOccupants)
				sneak(i,j,player,tempBoard)
				tempValue = getBoardValue(player,boardVals,tempBoard)
				if tempValue > bestValue:
					bestRow = i
					bestCol = j
					bestValue = tempValue
	#when we've tried every move, make the best move (if we found one), and print it
	if not bestRow == -1 and not bestCol == -1:
		if isValidRaid(bestRow,bestCol,player,boardOccupants):
			raid(bestRow,bestCol,player,boardOccupants)
		elif isEmpty(bestRow,bestCol,boardOccupants):
			sneak(bestRow,bestCol,player,boardOccupants)
		printNextState(boardOccupants,outputFile)

#function call for max nodes
def miniMax(player, depth, cutoffDepth,boardVals,boardOccupants,outputFile,row,col,battle):
	#base case: hit cutoff depth, return the value of the current board
	if depth == cutoffDepth:
		value = getBoardValue(player,boardVals,boardOccupants)
		if not battle:
			log(row,col,depth,value)
		return value
	#decide if this is a max or min node based on depth
	if depth % 2 == 0:
		value = -sys.maxint-1;
		currentPlayer = player
		maximizer = True
	else:
		value = sys.maxint
		currentPlayer = getOpponent(player)
		maximizer = False
	#track best move found so far
	bestRow = -1
	bestCol = -1
	#iterates over every board location
	for i in range(0,len(boardOccupants)):
		for j in range(0,len(boardOccupants[0])):
			if isEmpty(i,j,boardOccupants):
				if not battle:
					log(row,col,depth,value)
				#make copy of the board, try the move
				tempBoard = copy.deepcopy(boardOccupants)
				if isValidRaid(i,j,currentPlayer,tempBoard):
					raid(i,j,currentPlayer,tempBoard)
				else:
					sneak(i,j,currentPlayer,tempBoard)
				#look further down the tree with recursive call
				tempValue = miniMax(player,depth + 1, cutoffDepth,boardVals,tempBoard,outputFile,i,j,battle)
				#if max node and found new max, record it. opposite with min node
				if maximizer and tempValue > value:
					bestRow = i
					bestCol = j
					value = tempValue
				elif not maximizer and tempValue < value:
					bestRow = i
					bestCol = j
					value = tempValue
	if not battle:
		log(row,col,depth,value)
	#if we're at the root, examine the best move, make it, print state
	if depth == 0 and not bestRow == -1 and not bestCol == -1:
		if isValidRaid(bestRow,bestCol,player,boardOccupants) :
			raid(bestRow,bestCol,player,boardOccupants)
		elif isEmpty(bestRow,bestCol,boardOccupants):
			sneak(bestRow,bestCol,player,boardOccupants)
		printNextState(boardOccupants,outputFile)
	return value

#alpha beta pruning search algorithm
#function call for max nodes
def alphabeta(player, depth, cutoffDepth,boardVals, boardOccupants,outputFile,row,col,alpha,beta,battle):
	#base case: hit cutoff depth, return the value of the current board
	if depth == cutoffDepth:
		value = getBoardValue(player,boardVals,boardOccupants)
		if not battle:
			logab(row,col,depth,value,alpha,beta)
		return value
	#decide if this is a max or min node based on depth
	if depth % 2 == 0:
		value = -sys.maxint-1;
		currentPlayer = player
		maximizer = True
	else:
		value = sys.maxint
		currentPlayer = getOpponent(player)
		maximizer = False
	bestRow = -1
	bestCol = -1
	#iterates over every board location
	for i in range(0,len(boardOccupants)):
		for j in range(0,len(boardOccupants[0])):
			if isEmpty(i,j,boardOccupants):
				#is it worth checking other places? look at node value and alpha/beta
				if maximizer and value >= beta:
					if not battle:
						logab(row,col,depth,value,outputFile,alpha,beta)
					return value
				elif not maximizer and value <= alpha:
					if not battle:
						logab(row,col,depth,value,alpha,beta)
					return value
				#update alpha if max node and appropriate value
				if maximizer and value > alpha:
					alpha = value
				#update beta if min node and appropriate value
				if not maximizer and value < beta:
					beta = value
				if not battle:
					logab(row,col,depth,value,alpha,beta)
				#make copy of board, make move to be examined
				tempBoard = copy.deepcopy(boardOccupants)
				if isValidRaid(i,j,currentPlayer,tempBoard):
					raid(i,j,currentPlayer,tempBoard)
				else:
					sneak(i,j,currentPlayer,tempBoard)
				#recursive call to look further down the tree
				tempValue = alphabeta(player,depth + 1, cutoffDepth,boardVals,tempBoard,outputFile,i,j,alpha,beta,battle)
				#update best move if appropriate
				if maximizer and tempValue > value:
					bestRow = i
					bestCol = j
					value = tempValue
				elif not maximizer and tempValue < value:
					bestRow = i
					bestCol = j
					value = tempValue
	if not battle:
		logab(row,col,depth,value,alpha,beta)
	#if we're at the root, examine the best move, make it, print state
	if depth == 0 and not bestRow == -1 and not bestCol == -1:
		if isValidRaid(bestRow,bestCol,player,boardOccupants) :
			raid(bestRow,bestCol,player,boardOccupants)
		elif isEmpty(bestRow,bestCol,boardOccupants):
			sneak(bestRow,bestCol,player,boardOccupants)
		printNextState(boardOccupants,outputFile)
	return value

def battle(firstPlayer, firstPlayerAlg, firstPlayerCutoff, secondPlayer, secondPlayerAlg, secondPlayerCutoff, boardVals, boardOccupants,outputFile):
	#start with first player
	firstPlayersTurn = True
	#decide if board is full by examining each square
	boardFull = True
	for i in range(0,len(boardOccupants)):
		for j in range(0,len(boardOccupants[0])):
			if boardOccupants[i][j] == '*':
				boardFull = False
	#while the board is not full, make a move for the correct player
	while not boardFull:
		if firstPlayersTurn:
			if firstPlayerAlg == 1:
				greedyBestFirst(firstPlayer, boardVals, boardOccupants,outputFile)
			elif firstPlayerAlg == 2:
				miniMax(firstPlayer, 0, firstPlayerCutoff,boardVals,boardOccupants,outputFile,0,0,True)
			elif firstPlayerAlg == 3:
				alphabeta(firstPlayer, 0, firstPlayerCutoff,boardVals,boardOccupants,outputFile,0,0,-sys.maxint-1,sys.maxint,True)
		else:
			if secondPlayerAlg == 1:
				greedyBestFirst(secondPlayer, boardVals, boardOccupants, outputFile)
			elif secondPlayerAlg == 2:
				miniMax(secondPlayer, 0, secondPlayerCutoff,boardVals,boardOccupants,outputFile,0,0,True)
			elif secondPlayerAlg == 3:
				alphabeta(secondPlayer, 0, secondPlayerCutoff,boardVals,boardOccupants,outputFile,0,0,-sys.maxint-1,sys.maxint,True)
		#decide if board is full now
		boardFull = True
		for i in range(0,len(boardOccupants)):
			for j in range(0,len(boardOccupants[0])):
				if boardOccupants[i][j] == '*':
					boardFull = False
		#switch player
		firstPlayersTurn = not firstPlayersTurn

#main driver function
def main(argv):
	with open(argv[1]) as inputFile:
		task = int(inputFile.readline())
		if task == 4:
			firstPlayer = inputFile.readline().strip()
			firstPlayerAlg = int(inputFile.readline())
			firstPlayerCutoff = int(inputFile.readline())
			secondPlayer = inputFile.readline().strip()
			secondPlayerAlg = int(inputFile.readline())
			secondPlayerCutoff = int(inputFile.readline())
		else:
			player = inputFile.readline().strip()
			cutoffDepth = int(inputFile.readline())
		
		boardVals = []
		for i in range(0,5):
			boardVals.append(inputFile.readline().split())
		boardOccupants = []
		for i in range(0,5):
			boardOccupants.append(list(inputFile.readline().strip()))

	if task == 1:
		with open('next_state.txt','w+') as outputFile:
			greedyBestFirst(player,boardVals,boardOccupants,outputFile)
			removeLastChar(outputFile)
			outputFile.close()
	elif task == 2:
		with open('traverse_log.txt','w+') as f:
			f.write('Node,Depth,Value\n')
			f.close()
		with open('next_state.txt','w+') as outputFile:
			miniMax(player,0,cutoffDepth,boardVals,boardOccupants,outputFile,0,0,False)
			removeLastChar(outputFile)
			outputFile.close()
		with open('traverse_log.txt','rb+') as t:
			removeLastChar(t)
			t.close()
	elif task == 3:
		with open('traverse_log.txt','w+') as f:
			f.write('Node,Depth,Value,Alpha,Beta\n')
			f.close()
		with open('next_state.txt','w+') as outputFile:
			alphabeta(player,0,cutoffDepth,boardVals,boardOccupants,outputFile,0,0,-sys.maxint-1,sys.maxint,False)
			removeLastChar(outputFile)
			outputFile.close()
		with open('traverse_log.txt','rb+') as t:
			removeLastChar(t)
			t.close()
	elif task == 4:
		with open('trace_state.txt','w+') as outputFile:
			battle(firstPlayer, firstPlayerAlg, firstPlayerCutoff, secondPlayer, secondPlayerAlg, secondPlayerCutoff, boardVals, boardOccupants,outputFile)
			removeLastChar(outputFile)
			outputFile.close()

main(sys.argv[1:]);