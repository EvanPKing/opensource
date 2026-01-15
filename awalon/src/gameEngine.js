const ROLES = ["MERLIN", "PERCIVAL", "SERVANT", "MORGANA", "ASSASSIN"]

const ROLE_FACTION = {
  MERLIN: "GOOD",
  PERCIVAL: "GOOD",
  SERVANT: "GOOD",
  MORGANA: "EVIL",
  ASSASSIN: "EVIL"
}

const PLAYER_IDS = ["HUMAN", "BOT_1", "BOT_2", "BOT_3", "BOT_4"]

const MISSION_CONFIG = [2, 3, 2, 3, 3]

function shuffle(array) {
  const arr = [...array]
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

function createPlayers(humanRole) {
  const remainingRoles = ROLES.filter(r => r !== humanRole)
  const shuffled = shuffle(remainingRoles)
  const players = []
  players.push({
    id: "HUMAN",
    name: "你",
    role: humanRole,
    faction: ROLE_FACTION[humanRole],
    isHuman: true
  })
  for (let i = 0; i < 4; i++) {
    const role = shuffled[i]
    players.push({
      id: PLAYER_IDS[i + 1],
      name: `Bot_${i + 1}`,
      role,
      faction: ROLE_FACTION[role],
      isHuman: false
    })
  }
  return players
}

function buildPrivateInfo(players) {
  const info = {}
  const evilPlayers = players.filter(p => p.faction === "EVIL")
  const merlin = players.find(p => p.role === "MERLIN")
  const morgana = players.find(p => p.role === "MORGANA")
  const assassin = players.find(p => p.role === "ASSASSIN")
  const percival = players.find(p => p.role === "PERCIVAL")

  for (const p of players) {
    const list = []
    list.push(`你是${p.role}，属于${p.faction}阵营。`)
    if (p.role === "MERLIN") {
      const others = evilPlayers.filter(e => e.id !== p.id)
      if (others.length > 0) {
        const ids = others.map(e => e.id).join("，")
        list.push(`你知道以下玩家是红方：${ids}。`)
      }
    } else if (p.role === "PERCIVAL") {
      const candidates = []
      if (merlin) candidates.push(merlin.id)
      if (morgana) candidates.push(morgana.id)
      if (candidates.length > 0) {
        const ids = candidates.join("，")
        list.push(`你知道以下玩家中分别是梅林和莫甘娜，但不知道谁是谁：${ids}。`)
      }
    } else if (p.faction === "EVIL") {
      const others = evilPlayers.filter(e => e.id !== p.id)
      if (others.length > 0) {
        const ids = others.map(e => e.id).join("，")
        list.push(`你知道以下玩家和你同为红方：${ids}。`)
      }
    }
    if (assassin && p.id === assassin.id) {
      list.push("如果蓝方先完成3个任务，你将获得一次刺杀机会。")
    }
    info[p.id] = list
  }
  return info
}

function createInitialGameState(humanRole) {
  const players = createPlayers(humanRole)
  const leaderIndex = Math.floor(Math.random() * players.length)
  const privateInfo = buildPrivateInfo(players)
  return {
    players,
    leaderIndex,
    currentRound: 1,
    missions: [],
    successCount: 0,
    failCount: 0,
    consecutiveRejects: 0,
    status: "ONGOING",
    speechLog: [],
    privateInfo
  }
}

function getPublicState(state) {
  return {
    players: state.players.map(p => ({
      id: p.id,
      name: p.name,
      isHuman: p.isHuman,
      faction: p.isHuman ? p.faction : undefined
    })),
    leaderIndex: state.leaderIndex,
    currentRound: state.currentRound,
    missions: state.missions,
    successCount: state.successCount,
    failCount: state.failCount,
    consecutiveRejects: state.consecutiveRejects,
    status: state.status,
    speechLog: state.speechLog
  }
}

function startNewMission(state, team) {
  const mission = {
    round: state.currentRound,
    team,
    votes: {},
    approved: false,
    cards: {},
    result: null
  }
  state.missions.push(mission)
  return mission
}

function applyVotes(state, mission, votes) {
  mission.votes = votes
  const yesCount = Object.values(votes).filter(v => v === "YES").length
  if (yesCount > state.players.length / 2) {
    mission.approved = true
    state.consecutiveRejects = 0
  } else {
    mission.approved = false
    state.consecutiveRejects += 1
  }
}

function applyMissionCards(state, mission, cards) {
  mission.cards = cards
  const fails = Object.values(cards).filter(c => c === "FAIL").length
  if (fails > 0) {
    mission.result = "FAIL"
    state.failCount += 1
  } else {
    mission.result = "SUCCESS"
    state.successCount += 1
  }
}

function advanceAfterMission(state) {
  if (state.failCount >= 3) {
    state.status = "EVIL_WIN"
    return
  }
  if (state.successCount >= 3) {
    state.status = "ASSASSIN_PHASE"
    return
  }
  state.currentRound += 1
  state.leaderIndex = (state.leaderIndex + 1) % state.players.length
}

function performAssassination(state, targetId) {
  const target = state.players.find(p => p.id === targetId)
  if (!target) return
  if (target.role === "MERLIN") {
    state.status = "EVIL_WIN"
  } else {
    state.status = "GOOD_WIN"
  }
}

module.exports = {
  PLAYER_IDS,
  MISSION_CONFIG,
  createInitialGameState,
  getPublicState,
  startNewMission,
  applyVotes,
  applyMissionCards,
  advanceAfterMission,
  performAssassination
}

