import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  Plus, Trash2, ChevronRight, CheckCircle2, 
  Circle, AlertCircle, Clock, Users, 
  XOctagon, LayoutGrid, ListTodo, Trash,
  BarChart3, Settings2, Info, Edit3, Save, X
} from 'lucide-react';

const App = () => {
  // 초기 데이터 또는 로컬 스토리지에서 불러오기
  const [tasks, setTasks] = useState(() => {
    const saved = localStorage.getItem('eisenhower-tasks');
    return saved ? JSON.parse(saved) : [
      { id: 1, text: '이번 주 주간 보고서 작성', quadrant: 1, completed: false, createdAt: Date.now() },
      { id: 2, text: '외국어 공부 30분', quadrant: 2, completed: false, createdAt: Date.now() },
      { id: 3, text: '불필요한 회의 일정 조정', quadrant: 3, completed: false, createdAt: Date.now() },
      { id: 4, text: '유튜브 무한 스크롤 방지', quadrant: 4, completed: false, createdAt: Date.now() },
    ];
  });

  const [newTask, setNewTask] = useState('');
  const [selectedQuadrant, setSelectedQuadrant] = useState(1);
  const [activeTab, setActiveTab] = useState('matrix'); // 'matrix' or 'list'
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  // 데이터 변경 시 로컬 스토리지 저장
  useEffect(() => {
    localStorage.setItem('eisenhower-tasks', JSON.stringify(tasks));
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
    setTasks([task, ...tasks]);
    setNewTask('');
  };

  const toggleTask = (id) => {
    setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  };

  const deleteTask = (id) => {
    setTasks(tasks.filter(t => t.id !== id));
  };

  const startEdit = (task) => {
    setEditingId(task.id);
    setEditText(task.text);
  };

  const saveEdit = () => {
    setTasks(tasks.map(t => t.id === editingId ? { ...t, text: editText } : t));
    setEditingId(null);
  };

  const moveTask = (id) => {
    setTasks(tasks.map(t => {
      if (t.id === id) {
        return { ...t, quadrant: t.quadrant === 4 ? 1 : t.quadrant + 1 };
      }
      return t;
    }));
  };

  const clearCompleted = () => {
    setTasks(tasks.filter(t => !t.completed));
  };

  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    const quadrantCounts = [1, 2, 3, 4].map(q => tasks.filter(t => t.quadrant === q).length);
    return { total, completed, quadrantCounts, percent: total > 0 ? Math.round((completed / total) * 100) : 0 };
  }, [tasks]);

  return (
    <div className="min-h-screen bg-[#F1F5F9] text-slate-900 font-sans pb-20">
      {/* Top Navbar */}
      <nav className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-blue-700 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-100">
              <LayoutGrid size={22} strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tight text-slate-800 leading-none">Eisenhower <span className="text-indigo-600">Pro</span></h1>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">Focus on what matters</p>
            </div>
          </div>
          <div className="flex bg-slate-100 p-1.5 rounded-2xl">
            <button 
              onClick={() => setActiveTab('matrix')}
              className={`flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'matrix' ? 'bg-white shadow-md text-indigo-600 scale-105' : 'text-slate-500 hover:text-slate-700'}`}
            >
              <LayoutGrid size={16} /> 매트릭스
            </button>
            <button 
              onClick={() => setActiveTab('list')}
              className={`flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'list' ? 'bg-white shadow-md text-indigo-600 scale-105' : 'text-slate-500 hover:text-slate-700'}`}
            >
              <ListTodo size={16} /> 전체 목록
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-10">
        {/* Input Form Section */}
        <div className="max-w-3xl mx-auto mb-12">
           <form onSubmit={addTask} className="group">
            <div className="bg-white p-2 pl-6 rounded-3xl border-2 border-slate-200 shadow-xl shadow-slate-200/50 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-50 transition-all flex items-center gap-4">
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="어떤 일을 완료해야 하나요?"
                className="flex-1 bg-transparent py-4 outline-none text-slate-700 font-bold text-lg placeholder:text-slate-300"
              />
              <div className="hidden sm:flex items-center gap-2 bg-slate-50 py-2 px-4 rounded-2xl border border-slate-100">
                <span className="text-[10px] font-black text-slate-400 uppercase">분류:</span>
                <select 
                  value={selectedQuadrant}
                  onChange={(e) => setSelectedQuadrant(Number(e.target.value))}
                  className="bg-transparent text-xs font-black outline-none cursor-pointer text-indigo-600"
                >
                  {quadrants.map(q => <option key={q.id} value={q.id}>Q{q.id} - {q.label}</option>)}
                </select>
              </div>
              <button 
                type="submit"
                disabled={!newTask.trim()}
                className="bg-indigo-600 text-white p-4 rounded-2xl hover:bg-indigo-700 disabled:opacity-30 disabled:hover:bg-indigo-600 transition-all shadow-lg shadow-indigo-200"
              >
                <Plus size={24} strokeWidth={3} />
              </button>
            </div>
          </form>
        </div>

        {activeTab === 'matrix' ? (
          <div className="relative">
            {/* Axis Labels */}
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-white px-4 py-1 rounded-full border border-slate-200 z-10">
              긴급도 (Urgency)
            </div>
            <div className="absolute top-1/2 -left-8 -translate-y-1/2 -rotate-90 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-white px-4 py-1 rounded-full border border-slate-200 z-10 hidden xl:block">
              중요도 (Importance)
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative">
              {/* Central Divider Decorations */}
              <div className="hidden lg:block absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-0 right-0 h-px bg-slate-200 -translate-y-1/2"></div>
                <div className="absolute left-1/2 top-0 bottom-0 w-px bg-slate-200 -translate-x-1/2"></div>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-[#F1F5F9] border-4 border-white rounded-full flex items-center justify-center">
                  <div className="w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
                </div>
              </div>

              {quadrants.map((q) => (
                <div key={q.id} className={`flex flex-col bg-white rounded-[2.5rem] border-2 ${q.borderColor} overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 group/card`}>
                  <div className={`p-6 flex items-center justify-between ${q.bgColor}`}>
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-2xl bg-white shadow-md flex items-center justify-center ${q.textColor}`}>
                        {q.icon}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-black px-2 py-0.5 rounded-md ${q.textColor} bg-white border border-current opacity-70`}>QUADRANT {q.id}</span>
                          <h3 className={`font-black text-lg ${q.textColor}`}>{q.title}</h3>
                        </div>
                        <p className="text-slate-500 text-xs font-bold mt-0.5">{q.label}</p>
                      </div>
                    </div>
                    <div className="text-right hidden sm:block">
                       <span className="text-3xl font-black text-slate-900/5 uppercase">{q.title.split(' ')[0]}</span>
                    </div>
                  </div>
                  
                  <div className="flex-1 p-6 space-y-4 min-h-[350px] max-h-[500px] overflow-y-auto custom-scrollbar bg-white">
                    {tasks.filter(t => t.quadrant === q.id).length === 0 ? (
                      <div className="h-full flex flex-col items-center justify-center py-20 grayscale opacity-20">
                        <div className="p-4 rounded-full border-2 border-dashed border-slate-400 mb-4">
                          {q.icon}
                        </div>
                        <p className="text-sm font-black italic">No tasks here yet.</p>
                      </div>
                    ) : (
                      tasks.filter(t => t.quadrant === q.id).map(task => (
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
                          qStyle={q}
                        />
                      ))
                    )}
                  </div>
                  
                  <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                    <p className="text-[10px] font-bold text-slate-400 italic">"{q.desc}"</p>
                    <span className="text-[10px] font-black text-slate-400 bg-white px-2 py-1 rounded-lg border border-slate-200">
                      {tasks.filter(t => t.quadrant === q.id).length} ITEMS
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-xl overflow-hidden">
             <div className="p-8 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
               <div>
                <h2 className="text-xl font-black text-slate-800">전체 작업 리스트</h2>
                <p className="text-sm text-slate-500 font-medium">등록된 모든 할 일을 시간순으로 관리하세요.</p>
               </div>
               <button 
                onClick={clearCompleted}
                className="flex items-center gap-2 px-6 py-2.5 bg-rose-50 text-rose-600 rounded-2xl text-sm font-black hover:bg-rose-100 transition-all border border-rose-100"
              >
                <Trash size={16} /> 완료된 항목 정리
              </button>
             </div>
             <div className="p-8 space-y-4 max-h-[70vh] overflow-y-auto">
               {tasks.length === 0 ? (
                 <div className="py-32 text-center">
                    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-300">
                      <ListTodo size={32} />
                    </div>
                    <p className="text-slate-400 font-bold">비어 있는 리스트입니다.</p>
                 </div>
               ) : (
                 tasks.map(task => (
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
                    qStyle={quadrants.find(q => q.id === task.quadrant)}
                    showQuadrantLabel
                  />
                 ))
               )}
             </div>
          </div>
        )}

        {/* Floating Stats Footer */}
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-8 py-4 rounded-[2rem] shadow-2xl flex items-center gap-8 z-50 border border-white/10">
          <div className="flex flex-col">
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Total Tasks</span>
            <span className="text-xl font-black">{stats.total}</span>
          </div>
          <div className="w-px h-8 bg-white/10"></div>
          <div className="flex flex-col flex-1 min-w-[120px]">
            <div className="flex justify-between items-end mb-1">
              <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Efficiency</span>
              <span className="text-xs font-black text-indigo-400">{stats.percent}%</span>
            </div>
            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-indigo-500 to-blue-400 transition-all duration-700" style={{ width: `${stats.percent}%` }}></div>
            </div>
          </div>
        </div>
      </main>
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #E2E8F0;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #CBD5E1;
        }
      `}</style>
    </div>
  );
};

const TaskItem = ({ 
  task, toggleTask, deleteTask, moveTask, qStyle, 
  showQuadrantLabel, startEdit, editingId, editText, setEditText, saveEdit 
}) => {
  const isEditing = editingId === task.id;

  return (
    <div className={`group flex items-center gap-4 p-5 rounded-[1.5rem] border-2 transition-all ${task.completed ? 'bg-slate-50/50 border-slate-100' : 'bg-white border-slate-50 shadow-sm hover:border-indigo-100 hover:shadow-indigo-100/30'}`}>
      <button 
        onClick={() => toggleTask(task.id)}
        className={`flex-shrink-0 transition-all transform hover:scale-110 ${task.completed ? 'text-indigo-500' : 'text-slate-200 hover:text-indigo-300'}`}
      >
        {task.completed ? <CheckCircle2 size={24} fill="currentColor" className="text-white fill-indigo-500" /> : <Circle size={24} />}
      </button>
      
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <div className="flex items-center gap-2">
            <input 
              autoFocus
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
              className="flex-1 bg-slate-100 px-3 py-1.5 rounded-lg font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button onClick={saveEdit} className="p-1.5 text-emerald-600 bg-emerald-50 rounded-md hover:bg-emerald-100">
              <Save size={16} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              {showQuadrantLabel && (
                <span className={`text-[8px] font-black px-1.5 py-0.5 rounded-md uppercase ${qStyle.textColor} ${qStyle.bgColor} border border-current opacity-70`}>
                  Q{task.quadrant}
                </span>
              )}
              <span className={`text-base font-bold truncate transition-all ${task.completed ? 'text-slate-300 line-through italic' : 'text-slate-700'}`}>
                {task.text}
              </span>
            </div>
            <span className="text-[10px] text-slate-300 font-medium mt-0.5">
              {new Date(task.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} 생성
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {!task.completed && (
          <>
            <button 
              onClick={() => startEdit(task)}
              className="p-2 text-slate-300 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all"
              title="편집"
            >
              <Edit3 size={16} />
            </button>
            <button 
              onClick={() => moveTask(task.id)}
              className="p-2 text-slate-300 hover:text-emerald-600 hover:bg-emerald-50 rounded-xl transition-all"
              title="다음 단계로 이동"
            >
              <ChevronRight size={16} />
            </button>
          </>
        )}
        <button 
          onClick={() => deleteTask(task.id)}
          className="p-2 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-all"
          title="삭제"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
};

export default App;
