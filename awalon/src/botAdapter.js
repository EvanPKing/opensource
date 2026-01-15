const fetch = (...args) => import("node-fetch").then(({ default: fetch }) => fetch(...args))

function buildDeepSeekMessages(payload) {
  const system = {
    role: "system",
    content:
      "你是一个阿瓦隆桌游玩家，请严格按照要求的输出格式作答，不要添加多余解释。所有决策都基于游戏规则进行推理，你的所有回答都必须基于HUMAN以及其他机器人的回复，并且用有利于自己游戏胜利的方式回答。"
  }
  const user = {
    role: "user",
    content: JSON.stringify(payload, null, 2)
  }
  return [system, user]
}

async function callDeepSeek(payload, instruction) {
  const apiKey = process.env.DEEPSEEK_API_KEY
  if (!apiKey) {
    throw new Error("DEEPSEEK_API_KEY 未设置")
  }
  const body = {
    model: "deepseek-chat",
    messages: buildDeepSeekMessages({ ...payload, instruction }),
    stream: false
  }
  const res = await fetch("https://api.deepseek.com/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify(body)
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`DeepSeek API error: ${res.status} ${text}`)
  }
  const data = await res.json()
  const content = data.choices?.[0]?.message?.content || ""
  return content.trim()
}

async function botSpeak(player, stateForBot, privateInfo) {
  const payload = {
    player_id: player.id,
    role: player.role,
    faction: player.faction,
    phase: "SPEECH",
    round: stateForBot.currentRound,
    leader: stateForBot.players[stateForBot.leaderIndex].id,
    required_team_size: stateForBot.requiredTeamSize,
    current_team: stateForBot.currentTeam || [],
    all_players: stateForBot.players,
    mission_history: stateForBot.missions,
    vote_history: stateForBot.voteHistory || [],
    speech_log: stateForBot.speechLog || [],
    private_info: privateInfo[player.id] || []
  }
  const instruction = "请用中文进行发言，可以表达怀疑、信任或策略，发言不超过200字。"
  return callDeepSeek(payload, instruction)
}

function cleanAndParseJson(text) {
  try {
    // 尝试直接解析
    return JSON.parse(text);
  } catch (e) {
    // 尝试提取 markdown 代码块
    const match = text.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
    if (match) {
      try {
        return JSON.parse(match[1]);
      } catch (e2) {}
    }
    // 尝试提取纯数组
    const arrayMatch = text.match(/\[.*\]/s);
    if (arrayMatch) {
      try {
        return JSON.parse(arrayMatch[0]);
      } catch (e3) {}
    }
  }
  return null;
}

async function botChooseTeam(player, stateForBot, privateInfo) {
  const payload = {
    player_id: player.id,
    role: player.role,
    faction: player.faction,
    phase: "TEAM_BUILD",
    round: stateForBot.currentRound,
    leader: player.id,
    required_team_size: stateForBot.requiredTeamSize,
    all_players: stateForBot.players,
    mission_history: stateForBot.missions,
    vote_history: stateForBot.voteHistory || [],
    speech_log: stateForBot.speechLog || [],
    private_info: privateInfo[player.id] || []
  }
  const instruction =
    `你是本轮队长，请只输出一个JSON数组，包含要上任务的玩家ID，例如：["HUMAN","BOT_1"]，不要添加其它文字。`
  
  const text = await callDeepSeek(payload, instruction)
  const arr = cleanAndParseJson(text);
  
  // 验证有效性，如果无效则随机生成一个队伍兜底
  if (Array.isArray(arr) && arr.length === stateForBot.requiredTeamSize) {
    return arr;
  }
  
  // 兜底策略：随机选人
  console.log(`Bot ${player.id} failed to choose valid team, using random fallback.`);
  const allIds = stateForBot.players.map(p => p.id);
  const shuffled = allIds.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, stateForBot.requiredTeamSize);
}

async function botVote(player, stateForBot, privateInfo) {
  const payload = {
    player_id: player.id,
    role: player.role,
    faction: player.faction,
    phase: "VOTE",
    round: stateForBot.currentRound,
    leader: stateForBot.players[stateForBot.leaderIndex].id,
    required_team_size: stateForBot.requiredTeamSize,
    current_team: stateForBot.currentTeam || [],
    all_players: stateForBot.players,
    mission_history: stateForBot.missions,
    vote_history: stateForBot.voteHistory || [],
    speech_log: stateForBot.speechLog || [],
    private_info: privateInfo[player.id] || []
  }
  const instruction =
    "你需要对当前队伍投票，请只输出 YES 或 NO，不要添加任何解释。"
  const text = await callDeepSeek(payload, instruction)
  if (text.includes("YES")) return "YES"
  if (text.includes("NO")) return "NO"
  return "YES"
}

async function botMissionCard(player, stateForBot, privateInfo) {
  const payload = {
    player_id: player.id,
    role: player.role,
    faction: player.faction,
    phase: "MISSION",
    round: stateForBot.currentRound,
    leader: stateForBot.players[stateForBot.leaderIndex].id,
    required_team_size: stateForBot.requiredTeamSize,
    current_team: stateForBot.currentTeam || [],
    all_players: stateForBot.players,
    mission_history: stateForBot.missions,
    private_info: privateInfo[player.id] || []
  }
  const instruction =
    "你正在执行任务，如果你是好人只能出 SUCCESS；如果你是红方可以在 SUCCESS 或 FAIL 中选择。请只输出 SUCCESS 或 FAIL。"
  const text = await callDeepSeek(payload, instruction)
  if (player.faction === "GOOD") return "SUCCESS"
  if (text.includes("FAIL")) return "FAIL"
  return "SUCCESS"
}

async function botAssassinate(player, stateForBot, privateInfo) {
  const payload = {
    player_id: player.id,
    role: player.role,
    faction: player.faction,
    phase: "ASSASSIN",
    round: stateForBot.currentRound,
    all_players: stateForBot.players,
    mission_history: stateForBot.missions,
    vote_history: stateForBot.voteHistory || [],
    speech_log: stateForBot.speechLog || [],
    private_info: privateInfo[player.id] || []
  }
  const instruction =
    "你是刺客，蓝方已经完成3个任务，请在所有玩家中选择你认为是梅林的人。只输出目标玩家ID，例如：\"HUMAN\"。"
  const text = await callDeepSeek(payload, instruction)
  return text.replace(/["\s]/g, "")
}

module.exports = {
  botSpeak,
  botChooseTeam,
  botVote,
  botMissionCard,
  botAssassinate
}

