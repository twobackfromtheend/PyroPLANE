

class ATeam:
    def __init__(self,teamName,games):
        pass
        
        
        
    def output_all(team):
        output = ''
        hitsTotal = len(team.hits)
        output += 'Total Hits: '+str(hitsTotal)+'\n'
        # hits
        hitsAttacking = sum(hit.half==1 for hit in team.hits)
        # hitsDefending = sum(hit.half==0 for hit in team.hits)
        output += '    Attacking Half: '+str(hitsAttacking)+' ('+"{:.1%}".format(hitsAttacking/hitsTotal)+')    Defending Half: '+str(hitsTotal-hitsAttacking)+' ('+"{:.1%}".format((hitsTotal-hitsAttacking)/hitsTotal)+')\n'
            # shots
        shotsTotal = sum(hit.shot>=1 for hit in team.hits)
        output +='Total Shots: '+str(shotsTotal)+' ('+"{:.1%}".format(shotsTotal/hitsTotal)+')\n'
        averageShotDistance = sum(hit.distance for hit in team.hits if hit.shot >=1)/shotsTotal
        output += '    Average Shot Distance: '+str(round(averageShotDistance))+'\n'
        goalsTotal = sum(hit.goal>=1 for hit in team.hits)
        output += '    Total Goals: '+str(goalsTotal)+' ('+"{:.1%}".format(goalsTotal/shotsTotal)+')\n'
        assistedTotal = sum(hit.goal==2 for hit in team.hits)
        output += '        Was Assisted: '+str(assistedTotal)+' ('+"{:.1%}".format(assistedTotal/goalsTotal)+')\n'
            # passes
        passesTotal = sum(hit.pass_>=1 for hit in team.hits)
        output += 'Total Passes: '+str(passesTotal)+' ('+"{:.1%}".format(passesTotal/hitsTotal)+')\n'
        assistsTotal = sum(hit.pass_==2 for hit in team.hits)
        output += '    Total Assists: '+str(assistsTotal)+' ('+"{:.1%}".format(assistsTotal/passesTotal)+')\n'
        secondAssistTotal = sum(hit.pass_==3 for hit in team.hits)
        output += '        Secondary Assists: '+str(secondAssistTotal)+' ('+"{:.1%}".format(secondAssistTotal/passesTotal)+')\n'
        averagePassDistance = sum(hit.distance for hit in team.hits if hit.pass_>=1)/passesTotal
        output += '    Average Pass Distance: '+str(round(averagePassDistance))+'\n'
            # dribbles
        dribblesTotal = sum(hit.dribble==1 for hit in team.hits)
        output += 'Total Dribbles: '+str(dribblesTotal)+' ('+"{:.1%}".format(dribblesTotal/hitsTotal)+')\n'
        averageDribbleDistance = sum(hit.distance for hit in team.hits if hit.dribble==1)/dribblesTotal
        output += '    Average Dribble Distance: '+str(round(averageDribbleDistance))+'\n'
            # saves
        savesTotal = sum(hit.save==1 for hit in team.hits)
        output += 'Total Saves: '+str(savesTotal)+' ('+"{:.1%}".format(savesTotal/hitsTotal)+')\n' 
        failedSavesTotal = sum(hit.save==-1 for hit in team.hits)
        output += '    Failed Saves: '+str(failedSavesTotal)+' ('+"{:.1%}".format(failedSavesTotal/hitsTotal)+')\n' 
        
        
        # possession
        output += '\n'
        output += 'Possession (by hit): ' + "{:.1%}".format(team.possession['h']) +'\n'
        output += 'Possession (by position): ' + "{:.1%}".format(team.possession['p']) +'\n'
        
        # position
        output += '\n'
        averagePosition = team.position['average']
        output += 'Average Position: ' + str(list(int(x) for x in team.averagePosition[0])) + '   v: ' + str(list(list(int(y) for y in x) for x in team.averagePosition[1]))+'\n'
        positionsTotal = team.position['total']
        inAttHalf = team.position['half'][1]
        output += 'In Attacking Half: '+"{:.1%}".format(inAttHalf/positionsTotal)+'    Defending Half: '+"{:.1%}".format(1-(inAttHalf/positionsTotal))
        inAttThird = team.position['third'][1]
        inMidThird = team.position['third'][0]
        inOwnThird = team.position['third'][-1]
        output += 'In Attacking Third: '+"{:.1%}".format(inAttThird/positionsTotal)+'    Middle Third: '+"{:.1%}".format(inMidThird/positionsTotal)+'    Defending Third: '+"{:.1%}".format(inOwnThird/positionsTotal)+'\n'
        onGround = team.position['height'][0]
        underGoal = team.position['height'][1]
        aboveGoal = team.position['height'][2]
        output += 'On Ground: '+"{:.1%}".format(onGround/positionsTotal)+'    Under Goal: '+"{:.1%}".format(underGoal/positionsTotal)+"    Above Goal: "+"{:.1%}".format(aboveGoal/positionsTotal)
        frontOfBall = team.position['ball']
        output += 'In Front of Ball:   3:'+"{:.1%}".format(frontOfBall[3]/positionsTotal)+'    2:'+"{:.1%}".format(frontOfBall[2]/positionsTotal)+'    1:'+"{:.1%}".format(frontOfBall[1]/positionsTotal)+'    0:'+"{:.1%}".format(frontOfBall[0]/positionsTotal)+'\n'
        
            
        # speed
        output += '\n'
        averageSpeed = team.speed['average']
        output += 'Average Speed: ' + str(round(averageSpeed)) + '\n'
        speedAttacking = team.speed['half'][1]
        speedDefending = team.speed['half'][0]
        output += '    In Attacking Half: ' + str(round(speedAttacking)) + '    In Defending Half: ' + str(round(speedDefending))
        
        output += '\n\n'

