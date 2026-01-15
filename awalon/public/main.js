const API_BASE = 'http://localhost:3001/api';

async function startGame() {
  const roleSelect = document.getElementById('humanRoleSelect');
  const role = roleSelect.value;

  window.humanRole = role;
  
  const res = await fetch(`${API_BASE}/game/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ humanRole: role })
  });
  
  const data = await res.json();
  if (data.error) {
    alert(data.error);
    return;
  }

  // 显示私有情报
  const privateBox = document.getElementById('private-info-box');
  const privateText = document.getElementById('privateInfoText');
  privateBox.classList.remove('hidden');
  privateText.innerHTML = data.privateInfo.map(line => `<div>${line}</div>`).join('');

  // 禁用开始按钮
  document.querySelector('#section-1-identity button').disabled = true;
  document.getElementById('humanRoleSelect').disabled = true;

  // 显示后续板块
  document.getElementById('section-2-speech').classList.remove('hidden');
  document.getElementById('section-3-log').classList.remove('hidden');
  document.getElementById('section-4-gameplay').classList.remove('hidden');
  if (role === 'ASSASSIN') {
    const assassinSection = document.getElementById('section-5-assassin');
    assassinSection.classList.remove('hidden');
    const assassinButton = document.querySelector('#assassin-controls button');
    if (assassinButton) assassinButton.disabled = true;
  }

  updateUI(data.state);
}

async function humanSpeak() {
  const input = document.getElementById('humanSpeechInput');
  const text = input.value.trim() || "（沉默）";
  
  const res = await fetch(`${API_BASE}/game/human/speak`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  
  const data = await res.json();
  input.value = ''; // 清空输入框
  updateUI(data.state);
}

async function botAutoTeam() {
  const btn = document.querySelector('#bot-team-build-area button');
  if (btn) {
    btn.disabled = true;
    btn.textContent = "机器人正在思考组队策略...";
  }

  try {
    const res = await fetch(`${API_BASE}/game/leader/auto-team`, { method: 'POST' });
    const data = await res.json();
    if (data.error) {
      alert("机器人组队失败：" + data.error);
    } else {
      updateUI(data.state);
    }
  } catch (e) {
    alert("请求机器人出错：" + e.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "让机器人队长自动组队";
    }
  }
}

async function humanSubmitTeam() {
  // 收集勾选的玩家
  const checkboxes = document.querySelectorAll('.player-checkbox input:checked');
  const team = Array.from(checkboxes).map(cb => cb.value);
  
  const res = await fetch(`${API_BASE}/game/human/choose-team`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ team })
  });
  
  const data = await res.json();
  if (data.error) {
    alert(data.error);
  } else {
    updateUI(data.state);
  }
}

async function humanVote(vote) {
  const res = await fetch(`${API_BASE}/game/vote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ humanVote: vote })
  });
  
  const data = await res.json();
  updateUI(data.state);
}

async function humanPlayCard(card) {
  const res = await fetch(`${API_BASE}/game/mission`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ humanCard: card })
  });
  
  const data = await res.json();
  
  // 弹窗提示任务结果
  if (data.lastMissionResult) {
    const { success, fails } = data.lastMissionResult;
    alert(`任务结果：\n成功票: ${success}\n失败票: ${fails}\n\n${fails > 0 ? "任务失败！" : "任务成功！"}`);
  }
  
  updateUI(data.state);
}

async function humanAssassinate() {
  const input = document.getElementById('assassinTarget');
  const targetId = input.value.trim();
  if (!targetId) {
    alert("请输入目标ID");
    return;
  }
  
  const res = await fetch(`${API_BASE}/game/assassinate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ targetId })
  });
  
  const data = await res.json();
  updateUI(data.state);
}

// 核心：更新界面状态
function updateUI(state) {
  if (!state) return;

  // 1. 更新顶部状态条 (Section 4)
  document.getElementById('round-display').textContent = state.currentRound;
  
  // 找队长名字
  const leader = state.players[state.leaderIndex];
  const isHumanLeader = leader.isHuman || leader.id === 'HUMAN';
  const leaderName = isHumanLeader ? "你 (HUMAN)" : leader.id;
  document.getElementById('leader-display').textContent = leaderName;

  document.getElementById('score-display').textContent = `${state.successCount} 胜 ${state.failCount} 负`;
  
  const need = [2, 3, 2, 3, 3][state.currentRound - 1]; // 简单的硬编码读取
  document.getElementById('team-size-display').textContent = need;

  // 2. 更新发言日志 (Section 3)
  const logDiv = document.getElementById('speech-log');
  if (state.speechLog && state.speechLog.length > 0) {
    logDiv.innerHTML = state.speechLog.map(log => {
      const isMe = log.from === 'HUMAN';
      return `
        <div class="speech-bubble" style="border-left: 4px solid ${isMe ? '#1890ff' : '#ddd'}">
          <strong>${log.from}</strong> <span class="role-tag">第${log.round}轮</span>
          <div>${log.text}</div>
        </div>
      `;
    }).join('');
    logDiv.scrollTop = logDiv.scrollHeight; // 滚动到底部
  } else {
    logDiv.innerHTML = '<div style="color: #999; font-style: italic;">暂无发言...</div>';
  }

  // 3. 控制不同阶段的显示/隐藏 (Section 4 & 5)
  const teamBuildArea = document.getElementById('team-build-area');
  const botTeamArea = document.getElementById('bot-team-build-area');
  const voteArea = document.getElementById('vote-area');
  const missionArea = document.getElementById('mission-area');
  const assassinSection = document.getElementById('section-5-assassin');
  const voteResultArea = document.getElementById('vote-result-area');
  const voteResultList = document.getElementById('vote-result-list');
  const missionHistoryArea = document.getElementById('mission-history-area');
  const missionHistoryBody = document.getElementById('mission-history-body');

  // 先全部隐藏，再按需显示
  teamBuildArea.classList.add('hidden');
  botTeamArea.classList.add('hidden');
  voteArea.classList.add('hidden');
  missionArea.classList.add('hidden');
  assassinSection.classList.add('hidden');
  if (voteResultArea) {
    voteResultArea.classList.add('hidden');
    if (voteResultList) voteResultList.innerHTML = '';
  }
  if (missionHistoryBody) {
    missionHistoryBody.innerHTML = '';
  }

  // 如果游戏结束
  if (state.status === 'GOOD_WIN') {
    alert("游戏结束：蓝方胜利！");
    return;
  }
  if (state.status === 'EVIL_WIN') {
    alert("游戏结束：红方胜利！");
    return;
  }

  // 刺杀阶段
  if (state.status === 'ASSASSIN_PHASE') {
    assassinSection.classList.remove('hidden');
    const assassinControls = document.getElementById('assassin-controls');
    const botAssassinControls = document.getElementById('bot-assassin-controls');
    const assassinButton = document.querySelector('#assassin-controls button');
    if (window.humanRole === 'ASSASSIN') {
      if (assassinControls) assassinControls.classList.remove('hidden');
      if (botAssassinControls) botAssassinControls.classList.add('hidden');
      if (assassinButton) assassinButton.disabled = false;
    } else {
      if (assassinControls) assassinControls.classList.add('hidden');
      if (botAssassinControls) botAssassinControls.classList.remove('hidden');
    }
    return;
  }

  // 正常回合流程
  // 看看当前是否有待投票的队伍
  const currentMission = state.missions[state.currentRound - 1];
  const hasPendingVote = currentMission && currentMission.team && currentMission.team.length > 0 && currentMission.approved === undefined;
  
  // 看看是否通过了投票，正在做任务
  const isMissionPhase = currentMission && currentMission.approved === true && !currentMission.result;

  if (isMissionPhase) {
      // 任务出牌阶段
    // 只有在队伍里的人才显示操作区
    const amInTeam = currentMission.team.includes('HUMAN');
    if (amInTeam) {
      missionArea.classList.remove('hidden');
    } else {
      missionArea.classList.remove('hidden');
      missionArea.innerHTML = "<p>正在执行任务... 你不在队伍中，等待结果。</p>";
    }
  
  } else if (hasPendingVote) {
    // 投票阶段
    voteArea.classList.remove('hidden');
    document.getElementById('current-team-display').textContent = currentMission.team.join(', ');

  } else {
      // 组队阶段
      // 重新计算 isHumanLeader，因为 updateUI 可能会比较长，确保逻辑一致
      const leader = state.players[state.leaderIndex];
      const isHumanLeader = leader.isHuman || leader.id === 'HUMAN';

      if (isHumanLeader) {
        teamBuildArea.classList.remove('hidden');
        // 生成勾选框 - 强制重新渲染，确保状态正确
        const container = document.getElementById('player-checkboxes');
        container.innerHTML = state.players.map(p => `
          <label class="player-checkbox">
            <input type="checkbox" value="${p.id}"> ${p.name || p.id}
          </label>
        `).join('');
      } else {
        botTeamArea.classList.remove('hidden');
      }
    }

  // 非刺杀阶段，如果你扮演刺客，则一直显示刺杀选项但禁用按钮
  if (window.humanRole === 'ASSASSIN' && state.status !== 'ASSASSIN_PHASE') {
    assassinSection.classList.remove('hidden');
    const assassinControls = document.getElementById('assassin-controls');
    const botAssassinControls = document.getElementById('bot-assassin-controls');
    const assassinButton = document.querySelector('#assassin-controls button');
    if (assassinControls) assassinControls.classList.remove('hidden');
    if (botAssassinControls) botAssassinControls.classList.add('hidden');
    if (assassinButton) assassinButton.disabled = true;
  }

  // 4. 更新最近一轮投票结果
  const missions = state.missions || [];
  if (voteResultArea && voteResultList && missions.length > 0) {
    const lastMission = missions[missions.length - 1];
    const votes = lastMission.votes || {};
    const voteKeys = Object.keys(votes);
    if (voteKeys.length > 0) {
      voteResultArea.classList.remove('hidden');
      const items = state.players.map(p => {
        const v = votes[p.id];
        if (!v) return null;
        const voteText = v === 'YES' ? '支持' : '反对';
        const isMe = p.id === 'HUMAN';
        const name = isMe ? '你 (HUMAN)' : (p.name || p.id);
        return `<li>${name}：${voteText}</li>`;
      }).filter(Boolean);
      voteResultList.innerHTML = items.join('');
    }
  }

  // 5. 更新所有任务历史表
  if (missionHistoryBody && missions.length > 0) {
    missions.forEach(m => {
      const teamNames = (m.team || []).map(id => {
        const player = state.players.find(p => p.id === id);
        return player ? (player.name || player.id) : id;
      }).join(', ');
      let resultText = '';
      if (m.result === 'SUCCESS') {
        resultText = '任务成功';
      } else if (m.result === 'FAIL') {
        resultText = '任务失败';
      } else if (m.approved === false) {
        resultText = '投票未通过';
      } else {
        resultText = '进行中';
      }
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="border:1px solid #eee; padding:4px; text-align:center;">${m.round}</td>
        <td style="border:1px solid #eee; padding:4px;">${teamNames}</td>
        <td style="border:1px solid #eee; padding:4px; text-align:center;">${resultText}</td>
      `;
      missionHistoryBody.appendChild(tr);
    });
  }
}

// 页面加载时拉取一次状态（如果是刷新页面的话）
// fetch(`${API_BASE}/game/state`).then(res => res.json()).then(updateUI).catch(() => {});
