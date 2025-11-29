// Sample tasks for the "Load Example" button
const sample = [
  {"title":"Fix login bug","due_date":"2025-11-30","estimated_hours":3,"importance":8,"dependencies":[]},
  {"title":"Write README","due_date":"2025-12-02","estimated_hours":1,"importance":6,"dependencies":[0]},
  {"title":"Hotfix payment","due_date":"2025-11-25","estimated_hours":4,"importance":9,"dependencies":[]}
];

document.getElementById('loadExample').addEventListener('click', ()=>{
  document.getElementById('taskInput').value = JSON.stringify(sample, null, 2);
});

document.getElementById('analyzeBtn').addEventListener('click', async ()=>{
  const raw = document.getElementById('taskInput').value.trim();
  let tasks = [];
  try{
    tasks = JSON.parse(raw);
    if(!Array.isArray(tasks)) throw new Error('Input must be a JSON array');
  }catch(e){
    alert('Invalid JSON: ' + e.message);
    return;
  }

  // Instead of calling a real backend, call the in-browser mock analyzer
  const results = mockAnalyze(tasks);
  displayResults(results);
});

function displayResults(results){
  const container = document.getElementById('results');
  container.innerHTML = '';
  for(const r of results){
    const div = document.createElement('div');
    div.className = 'task-card ' + (r.__score >= 100 ? 'high' : (r.__score >= 60 ? 'medium' : 'low'));
    div.innerHTML = `<div><strong>${r.title}</strong> <span class='score'>${r.__score}</span></div>
      <div>${r.__explanation}</div>
      <div style='font-size:12px;color:#666'>Due: ${r.due_date} • Est: ${r.estimated_hours}h • Importance: ${r.importance}</div>`;
    container.appendChild(div);
  }
}

// Mock analyzer ported from the scoring logic
function mockAnalyze(tasks){
  // Simple date parsing
  function parseDate(s){
    const d = new Date(s);
    if(isNaN(d)) return new Date('9999-12-31');
    return d;
  }
  const today = new Date();

  // detect circular dependencies
  const n = tasks.length;
  const graph = tasks.map(t => (t.dependencies || []).slice());
  const visited = new Array(n).fill(0);
  const inCycle = new Set();
  function dfs(u, stack){
    if(visited[u] === 1){
      const idx = stack.indexOf(u);
      if(idx !== -1){
        for(let i=idx;i<stack.length;i++) inCycle.add(stack[i]);
      }
      return;
    }
    if(visited[u] === 2) return;
    visited[u]=1; stack.push(u);
    for(const v of graph[u]||[]){ if(v>=0 && v<n) dfs(v, stack); }
    stack.pop(); visited[u]=2;
  }
  for(let i=0;i<n;i++) if(visited[i]===0) dfs(i, []);

  const results = tasks.map((t, idx)=>{
    const due = parseDate(t.due_date);
    const days = Math.ceil((due - today)/(1000*60*60*24));
    let score = 0;
    let expl = [];

    if(days < 0){ score += 120; expl.push('Overdue: +120'); }
    else if(days <=3){ score += 40; expl.push('Due soon: +40'); }
    else{ score += Math.max(0, 10 - Math.min(days,10)); expl.push(`Due in ${days} days`); }

    const importance = Number(t.importance||5);
    score += importance * 6; expl.push(`Importance ${importance}: +${importance*6}`);

    const est = Number(t.estimated_hours||1);
    if(est <=2){ score += 12; expl.push('Quick win: +12'); }
    else{ 
      const pen = Math.max(0,(est-2)*1.5); 
      score -= pen; 
      expl.push(`Effort penalty: -${pen.toFixed(1)}`); 
    }

    let dependents = 0; 
    for(const other of tasks){ 
      if((other.dependencies||[]).includes(idx)) dependents++; 
    }
    if(dependents>0){ score += 15*dependents; expl.push(`Has ${dependents} dependents: +${15*dependents}`); }

    if(inCycle.has(idx)){ score -= 10; expl.push('In circular dependency: -10'); }

    return Object.assign({}, t, {
      __score: Math.round(score*100)/100,
      __explanation: expl.join('; ')
    });
  });

  results.sort((a,b)=>b.__score - a.__score);
  return results;
}
