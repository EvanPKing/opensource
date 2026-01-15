const express = require("express")
const cors = require("cors")
const path = require("path")
require("dotenv").config()

const {
  PLAYER_IDS,
  MISSION_CONFIG,
  createInitialGameState,
  getPublicState,
  startNewMission,
  applyVotes,
  applyMissionCards,
  advanceAfterMission,
  performAssassination
} = require("./gameEngine")

const {
  botSpeak,
  botChooseTeam,
  botVote,
  botMissionCard,
  botAssassinate
} = require("./botAdapter")

const app = express()
const PORT = process.env.PORT || 3001

let gameState = null

app.use(cors())
app.use(express.json())
app.use(express.static(path.join(__dirname, "..", "public")))

app.post("/api/game/start", (req, res) => {
  const { humanRole } = req.body
  if (!humanRole) {
    return res.status(400).json({ error: "humanRole 必填" })
  }
  gameState = createInitialGameState(humanRole)
  res.json({
    state: getPublicState({
      ...gameState,
      requiredTeamSize: MISSION_CONFIG[gameState.currentRound - 1]
    }),
    privateInfo: gameState.privateInfo.HUMAN
  })
})

app.get("/api/game/state", (req, res) => {
  if (!gameState) {
    return res.status(400).json({ error: "游戏尚未开始" })
  }
  res.json({
    state: getPublicState({
      ...gameState,
      requiredTeamSize: MISSION_CONFIG[gameState.currentRound - 1]
    })
  })
})

app.post("/api/game/human/speak", async (req, res) => {
  if (!gameState) return res.status(400).json({ error: "游戏尚未开始" })
  const { text } = req.body
  if (!text) return res.status(400).json({ error: "text 必填" })
  const speech = {
    round: gameState.currentRound,
    order: gameState.speechLog.length + 1,
    from: "HUMAN",
    text
  }
  gameState.speechLog.push(speech)
  try {
    const requiredTeamSize = MISSION_CONFIG[gameState.currentRound - 1]
    for (const pid of PLAYER_IDS.slice(1)) {
      const player = gameState.players.find(p => p.id === pid)
      const text = await botSpeak(
        player,
        {
          ...getPublicState(gameState),
          requiredTeamSize,
          currentTeam: null,
          voteHistory: gameState.missions.map(m => ({
            round: m.round,
            team: m.team,
            votes: m.votes,
            approved: m.approved
          })),
          speechLog: gameState.speechLog
        },
        gameState.privateInfo
      )
      gameState.speechLog.push({
        round: gameState.currentRound,
        order: gameState.speechLog.length + 1,
        from: pid,
        text
      })
    }
    res.json({
      state: getPublicState({
        ...gameState,
        requiredTeamSize: MISSION_CONFIG[gameState.currentRound - 1]
      })
    })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

app.post("/api/game/human/choose-team", async (req, res) => {
  if (!gameState) return res.status(400).json({ error: "游戏尚未开始" })
  const { team } = req.body
  const requiredTeamSize = MISSION_CONFIG[gameState.currentRound - 1]
  if (!Array.isArray(team) || team.length !== requiredTeamSize) {
    return res.status(400).json({ error: `本轮需要选择 ${requiredTeamSize} 人` })
  }
  const mission = startNewMission(gameState, team)
  res.json({
    mission,
    state: getPublicState({
      ...gameState,
      requiredTeamSize
    })
  })
})

app.post("/api/game/leader/auto-team", async (req, res) => {
  if (!gameState) return res.status(400).json({ error: "游戏尚未开始" })
  const leader = gameState.players[gameState.leaderIndex]
  if (leader.id === "HUMAN") {
    return res.status(400).json({ error: "当前队长是你，请手动选人" })
  }
  const requiredTeamSize = MISSION_CONFIG[gameState.currentRound - 1]
  try {
    const team = await botChooseTeam(
      leader,
      {
        ...getPublicState(gameState),
        requiredTeamSize,
        voteHistory: gameState.missions.map(m => ({
          round: m.round,
          team: m.team,
          votes: m.votes,
          approved: m.approved
        })),
        speechLog: gameState.speechLog
      },
      gameState.privateInfo
    )
    const filtered = team.filter(id => PLAYER_IDS.includes(id)).slice(
      0,
      requiredTeamSize
    )
    if (filtered.length !== requiredTeamSize) {
      return res.status(500).json({ error: "机器人组队结果不合法" })
    }
    const mission = startNewMission(gameState, filtered)
    res.json({
      mission,
      state: getPublicState({
        ...gameState,
        requiredTeamSize
      })
    })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

app.post("/api/game/vote", async (req, res) => {
  if (!gameState) return res.status(400).json({ error: "游戏尚未开始" })
  if (gameState.missions.length === 0) {
    return res.status(400).json({ error: "尚未组队" })
  }
  const mission = gameState.missions[gameState.missions.length - 1]
  const { humanVote } = req.body
  if (humanVote !== "YES" && humanVote !== "NO") {
    return res.status(400).json({ error: "humanVote 必须是 YES 或 NO" })
  }
  const votes = { HUMAN: humanVote }
  const requiredTeamSize = MISSION_CONFIG[gameState.currentRound - 1]
  try {
    for (const pid of PLAYER_IDS.slice(1)) {
      const player = gameState.players.find(p => p.id === pid)
      const decision = await botVote(
        player,
        {
          ...getPublicState(gameState),
          requiredTeamSize,
          currentTeam: mission.team,
          voteHistory: gameState.missions.map(m => ({
            round: m.round,
            team: m.team,
            votes: m.votes,
            approved: m.approved
          })),
          speechLog: gameState.speechLog
        }),
        gameState.privateInfo
      )
      votes[pid] = decision
    }
    applyVotes(gameState, mission, votes)
    if (!mission.approved) {
      if (gameState.consecutiveRejects >= 5) {
        gameState.status = "EVIL_WIN"
      } else {
        gameState.leaderIndex =
          (gameState.leaderIndex + 1) % gameState.players.length
      }
    }
    res.json({
      mission,
      lastVoteResult: {
        approved: mission.approved,
        votes
      },
      state: getPublicState({
        ...gameState,
        requiredTeamSize: MISSION_CONFIG[gameState.currentRound - 1]
      })
    })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

app.post("/api/game/mission", async (req, res) => {
  if (!gameState) return res.status(400).json({ error: "游戏尚未开始" })
  if (gameState.missions.length === 0) {
    return res.status(400).json({ error: "尚未组队" })
  }
  const mission = gameState.missions[gameState.missions.length - 1]
  if (!mission.approved) {
    return res.status(400).json({ error: "当前队伍未通过投票" })
  }
  const { humanCard } = req.body
  const cards = {}
  const requiredTeamSize = MISSION_CONFIG[gameState.currentRound - 1]
  try {
    for (const pid of mission.team) {
      const player = gameState.players.find(p => p.id === pid)
      if (pid === "HUMAN") {
        if (player.faction === "GOOD") {
          cards[pid] = "SUCCESS"
        } else {
          if (humanCard !== "SUCCESS" && humanCard !== "FAIL") {
            return res.status(400).json({ error: "humanCard 必须是 SUCCESS 或 FAIL" })
          }
          cards[pid] = humanCard
        }
      } else {
        const decision = await botMissionCard(
          player,
          {
            ...getPublicState(gameState),
            requiredTeamSize,
            currentTeam: mission.team
          },
          gameState.privateInfo
        )
        cards[pid] = decision
      }
    }
    applyMissionCards(gameState, mission, cards)
    advanceAfterMission(gameState)
    res.json({
      mission: {
        round: mission.round,
        team: mission.team,
        result: mission.result
      },
      state: getPublicState({
        ...gameState,
        requiredTeamSize:
          gameState.status === "ONGOING"
            ? MISSION_CONFIG[gameState.currentRound - 1]
            : null
      })
    })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

app.post("/api/game/assassinate", async (req, res) => {
  if (!gameState) return res.status(400).json({ error: "游戏尚未开始" })
  if (gameState.status !== "ASSASSIN_PHASE") {
    return res.status(400).json({ error: "当前不在刺杀阶段" })
  }
  const assassin = gameState.players.find(p => p.role === "ASSASSIN")
  if (!assassin) return res.status(500).json({ error: "没有刺客" })
  const { targetId } = req.body
  if (assassin.id === "HUMAN") {
    if (!PLAYER_IDS.includes(targetId)) {
      return res.status(400).json({ error: "目标ID不合法" })
    }
    performAssassination(gameState, targetId)
    return res.json({
      status: gameState.status,
      state: getPublicState(gameState)
    })
  }
  try {
    const decision = await botAssassinate(
      assassin,
      {
        ...getPublicState(gameState),
        voteHistory: gameState.missions.map(m => ({
          round: m.round,
          team: m.team,
          votes: m.votes,
          approved: m.approved
        })),
        speechLog: gameState.speechLog
      },
      gameState.privateInfo
    )
    performAssassination(gameState, decision)
    res.json({
      assassinTarget: decision,
      status: gameState.status,
      state: getPublicState(gameState)
    })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

app.listen(PORT, () => {
  console.log(`Avalon server listening on http://localhost:${PORT}`)
})
