import React, { useState, useEffect, useMemo } from 'react';
import { 
  Plus, Trash2, ChevronRight, CheckCircle2, 
  Circle, AlertCircle, Clock, Users, 
  XOctagon, LayoutGrid, ListTodo, Trash,
  Info, Edit, Save, X
} from 'lucide-react';

const App = () => {
  // 브라우저 보안 정책(iframe 등)으로 인해 localStorage 접근이 막힐 경우를 대비한 안전한 가져오기
  const getStoredTasks = () => {
    try {
      const saved = localStorage.getItem('eisenhower-tasks-pro');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.warn("Storage access is restricted:", e);
    }
    // 기본 데이터
    return [
      { id: 1, text: '중요하고 긴급한 업무 (Do First)', quadrant: 1, completed: false, createdAt: Date.now() },
      { id: 2, text: '중요하지만 긴급하지 않은 계획 (Schedule)', quadrant: 2, completed: false, createdAt: Date.now() },
      { id: 3, text: '긴급하지만 중요하지 않은 업무 (Delegate)', quadrant: 3, completed: false, createdAt: Date.now() },
      { id: 4, text: '시간 낭비 요인 제거 (Eliminate)', quadrant: 4, completed: false, createdAt: Date.now() },
    ];
  };

  const [tasks, setTasks] = useState(getStoredTasks);
  const [newTask, setNewTask] = useState('');
  const [selectedQuadrant, setSelectedQuadrant] = useState(1);
  const [activeTab, setActiveTab] = useState('matrix'); 
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  // 안전하게 데이터 저장하기
  useEffect(() => {
    try {
      localStorage.setItem('eisenhower-tasks-pro', JSON.stringify(tasks));
    } catch (e) {
      // 저장 실패 시 무시 (사용자 환경 문제)
    }
  }, [tasks]);

  const quadrants = [
    { 
      id: 1, 
      title: 'Do First', 
      label: '중요함 & 긴급함',
      desc: '즉시 처리해야 할 위기 및 마감 업무',
      color: 'from-rose-500 to-red-600', 
      bgColor: 'bg-rose-50',
      textColor: 'text-rose-700',
      borderColor: 'border-rose-200',
      icon: <AlertCircle className="w-5 h-5" />
    },
    { 
      id: 2, 
      title: 'Schedule', 
      label: '중요함 & 긴급하지 않음',
      desc: '장기적 성공을 위한 계획 및 자기계발',
      color: 'from-emerald-500 to-teal-600', 
      bgColor: 'bg-emerald-50',
      textColor: 'text-emerald-700',
      borderColor: 'border-emerald-200',
      icon: <Clock className="w-5 h-5" />
    },
    { 
      id: 3, 
      title: 'Delegate', 
      label: '중요하지 않음 & 긴급함',
      desc: '다른 사람에게 위임 가능한 방해 요소',
      color: 'from-amber-400 to-orange-500', 
      bgColor: 'bg-amber-50',
      textColor: 'text-amber-700',
      borderColor: 'border-amber-200',
      icon: <Users className="w-5 h-5" />
    },
    { 
      id: 4, 
      title: 'Eliminate', 
      label: '중요하지 않음 & 긴급하지 않음',
      desc: '과감히 제거해야 할 시간 낭비 요인',
      color: 'from-slate-500 to-slate-700', 
      bgColor: 'bg-slate-100',
      textColor: 'text-slate-700',
      borderColor: 'border-slate-200',
      icon: <XOctagon className="w-5 h-5" />
    },
  ];

  const addTask = (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;
    const task = {
      id: Date.now(),
      text: newTask,
      quadrant: selectedQuadrant,
      completed: false,
      createdAt: Date.now()
    };
    setTasks(prev => [task, ...prev]);
    setNewTask('');
  };

  const toggleTask = (id) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  };

  const deleteTask = (id) => {
    setTasks(prev => prev.filter(t => t.id !== id));
  };

  const startEdit = (task) => {
    setEditingId(task.id);
    setEditText(task.text);
  };

  const saveEdit = () => {
    if (editText.trim()) {
      setTasks(prev => prev.map(t => t.id === editingId ? { ...t, text: editText } : t));
    }
    setEditingId(null);
  };

  const moveTask = (id) => {
    setTasks(prev => prev.map(t => {
      if (t.id === id) {
        return { ...t, quadrant: t.quadrant === 4 ? 1 : t.quadrant + 1 };
      }
      return t;
    }));
  };

  const clearCompleted = () => {
    setTasks(prev => prev.filter(t => !t.completed));
  };

  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    return { 
      total, 
      completed, 
      percent: total > 0 ? Math.round((completed / total) * 100) : 0 
    };
  }, [tasks]);

  return (
    <div className="min-h-screen bg-[#F1F5F9] text-slate-900 font-sans pb-24">
      {/* Header */}
      <nav className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg">
              <LayoutGrid size={22} />
            </div>
            <div>
              <h1 className="text-xl font-black text-slate-800 leading-none">Eisenhower <span className="text-indigo-600">Pro</span></h1>
            </div>
          </div>
          <div className="flex bg-slate-100 p-1 rounded-2xl">
            <button 
              onClick={() => setActiveTab('matrix')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'matrix' ? 'bg-white shadow-md text-indigo-600' : 'text-slate-500'}`}
            >
              매트릭스
            </button>
            <button 
              onClick={() => setActiveTab('list')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'list' ? 'bg-white shadow-md text-indigo-600' : 'text-slate-500'}`}
            >
              리스트
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-10">
        {/* Input */}
        <div className="max-w-3xl mx-auto mb-12">
          <form onSubmit={addTask} className="flex gap-4 bg-white p-2 pl-6 rounded-3xl border-2 border-slate-200 shadow-xl focus-within:border-indigo-500 transition-all">
            <input
              type="text"
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              placeholder="새로운 할 일을 입력하세요..."
              className="flex-1 bg-transparent py-3 outline-none text-slate-700 font-bold"
            />
            <select 
              value={selectedQuadrant}
              onChange={(e) => setSelectedQuadrant(Number(e.target.value))}
              className="hidden sm:block bg-slate-50 text-xs font-black outline-none cursor-pointer text-indigo-600 px-3 rounded-xl"
            >
              {quadrants.map(q => <option key={q.id} value={q.id}>Q{q.id} - {q.label}</option>)}
            </select>
            <button 
              type="submit"
              disabled={!newTask.trim()}
              className="bg-indigo-600 text-white p-3 rounded-2xl hover:bg-indigo-700 disabled:opacity-30 shadow-lg"
            >
              <Plus size={24} />
            </button>
          </form>
        </div>

        {activeTab === 'matrix' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {quadrants.map((q) => (
              <div key={q.id} className={`flex flex-col bg-white rounded-3xl border-2 ${q.borderColor} overflow-hidden shadow-sm`}>
                <div className={`p-6 flex items-center justify-between ${q.bgColor}`}>
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-2xl bg-white shadow-md flex items-center justify-center ${q.textColor}`}>
                      {q.icon}
                    </div>
                    <div>
                      <h3 className={`font-black text-lg ${q.textColor}`}>{q.title}</h3>
                      <p className="text-slate-500 text-xs font-bold">{q.label}</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex-1 p-6 space-y-4 min-h-[300px] max-h-[450px] overflow-y-auto">
                  {tasks.filter(t => t.quadrant === q.id).map(task => (
                    <TaskItem 
                      key={task.id} 
                      task={task} 
                      toggleTask={toggleTask} 
                      deleteTask={deleteTask} 
                      moveTask={moveTask}
                      startEdit={startEdit}
                      editingId={editingId}
                      editText={editText}
                      setEditText={setEditText}
                      saveEdit={saveEdit}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8 space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-black text-slate-800">전체 리스트</h2>
              <button onClick={clearCompleted} className="text-xs font-black text-rose-500 hover:bg-rose-50 px-3 py-1.5 rounded-lg border border-rose-100 transition-colors">
                완료 항목 정리
              </button>
            </div>
            {tasks.map(task => (
              <TaskItem 
                key={task.id} 
                task={task} 
                toggleTask={toggleTask} 
                deleteTask={deleteTask} 
                moveTask={moveTask}
                startEdit={startEdit}
                editingId={editingId}
                editText={editText}
                setEditText={setEditText}
                saveEdit={saveEdit}
                showQuadrantLabel
                qLabel={`Q${task.quadrant}`}
              />
            ))}
          </div>
        )}

        {/* Stats Footer */}
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-8 py-4 rounded-3xl shadow-2xl flex items-center gap-8 z-50">
          <div className="flex flex-col text-center">
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Total</span>
            <span className="text-xl font-black">{stats.total}</span>
          </div>
          <div className="w-px h-8 bg-white/10"></div>
          <div className="flex flex-col text-center">
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Progress</span>
            <span className="text-xl font-black text-indigo-400">{stats.percent}%</span>
          </div>
        </div>
      </main>
    </div>
  );
};

const TaskItem = ({ 
  task, toggleTask, deleteTask, moveTask, 
  showQuadrantLabel, qLabel, startEdit, editingId, editText, setEditText, saveEdit 
}) => {
  const isEditing = editingId === task.id;

  return (
    <div className={`group flex items-center gap-4 p-4 rounded-2xl border-2 transition-all ${task.completed ? 'bg-slate-50 border-slate-100 opacity-60' : 'bg-white border-slate-50 shadow-sm hover:border-indigo-100'}`}>
      <button onClick={() => toggleTask(task.id)} className={`flex-shrink-0 transition-transform hover:scale-110 ${task.completed ? 'text-indigo-500' : 'text-slate-200'}`}>
        {task.completed ? <CheckCircle2 size={24} fill="currentColor" className="text-white fill-indigo-500" /> : <Circle size={24} />}
      </button>
      
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <input 
            autoFocus
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onBlur={saveEdit}
            onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
            className="w-full bg-slate-100 px-3 py-1 rounded-lg font-bold outline-none"
          />
        ) : (
          <div className="flex items-center gap-2">
            {showQuadrantLabel && <span className="text-[10px] font-black px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 border border-slate-200">{qLabel}</span>}
            <span className={`text-base font-bold truncate ${task.completed ? 'line-through italic text-slate-400' : 'text-slate-700'}`}>{task.text}</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {!task.completed && (
          <>
            <button onClick={() => startEdit(task)} className="p-2 text-slate-300 hover:text-indigo-600"><Edit size={16} /></button>
            <button onClick={() => moveTask(task.id)} className="p-2 text-slate-300 hover:text-emerald-600"><ChevronRight size={16} /></button>
          </>
        )}
        <button onClick={() => deleteTask(task.id)} className="p-2 text-slate-300 hover:text-rose-500"><Trash2 size={16} /></button>
      </div>
    </div>
  );
};

export default App;
