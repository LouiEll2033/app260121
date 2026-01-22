import React, { useState, useEffect, useMemo } from 'react';
import { 
  Plus, Trash2, ChevronRight, CheckCircle2, 
  Circle, AlertCircle, Clock, Users, 
  XOctagon, LayoutGrid, ListTodo, Trash,
  BarChart3, Settings2, Info
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

  // 데이터 변경 시 로컬 스토리지 저장
  useEffect(() => {
    localStorage.setItem('eisenhower-tasks', JSON.stringify(tasks));
  }, [tasks]);

  const quadrants = [
    { 
      id: 1, 
      title: 'Do First', 
      label: '즉시 실행',
      desc: '긴급 & 중요',
      color: 'from-red-500 to-orange-500', 
      bgColor: 'bg-red-50',
      textColor: 'text-red-700',
      borderColor: 'border-red-200',
      icon: <AlertCircle className="w-5 h-5" />
    },
    { 
      id: 2, 
      title: 'Schedule', 
      label: '계획 수립',
      desc: '중요하나 긴급하지 않음',
      color: 'from-blue-500 to-indigo-500', 
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-700',
      borderColor: 'border-blue-200',
      icon: <Clock className="w-5 h-5" />
    },
    { 
      id: 3, 
      title: 'Delegate', 
      label: '권한 위임',
      desc: '긴급하나 중요하지 않음',
      color: 'from-amber-500 to-yellow-500', 
      bgColor: 'bg-amber-50',
      textColor: 'text-amber-700',
      borderColor: 'border-amber-200',
      icon: <Users className="w-5 h-5" />
    },
    { 
      id: 4, 
      title: 'Eliminate', 
      label: '삭제/제거',
      desc: '긴급하지도 중요하지도 않음',
      color: 'from-slate-500 to-gray-700', 
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

  // 통계 데이터 계산
  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    const quadrantCounts = [1, 2, 3, 4].map(q => tasks.filter(t => t.quadrant === q).length);
    return { total, completed, quadrantCounts, percent: total > 0 ? Math.round((completed / total) * 100) : 0 };
  }, [tasks]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans pb-20">
      {/* Top Navbar */}
      <nav className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white">
              <LayoutGrid size={18} strokeWidth={2.5} />
            </div>
            <h1 className="text-xl font-extrabold tracking-tight text-slate-800">Eisenhower <span className="text-indigo-600">Pro</span></h1>
          </div>
          <div className="flex bg-slate-100 p-1 rounded-xl">
            <button 
              onClick={() => setActiveTab('matrix')}
              className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-all ${activeTab === 'matrix' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500 hover:text-slate-700'}`}
            >
              매트릭스
            </button>
            <button 
              onClick={() => setActiveTab('list')}
              className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-all ${activeTab === 'list' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500 hover:text-slate-700'}`}
            >
              전체 목록
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 pt-8">
        {/* Statistics Dashboard */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <p className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">전체 할 일</p>
            <div className="flex items-end gap-2">
              <span className="text-3xl font-black text-slate-800">{stats.total}</span>
              <span className="text-slate-400 text-sm mb-1">건</span>
            </div>
          </div>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <p className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">진행률</p>
            <div className="flex items-end gap-2">
              <span className="text-3xl font-black text-indigo-600">{stats.percent}%</span>
              <div className="flex-1 h-2 bg-slate-100 rounded-full mb-2 overflow-hidden">
                <div className="h-full bg-indigo-500 transition-all duration-500" style={{ width: `${stats.percent}%` }}></div>
              </div>
            </div>
          </div>
          <div className="md:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div className="flex gap-4">
              {quadrants.map((q, i) => (
                <div key={q.id} className="text-center">
                  <div className={`w-2 h-8 mx-auto rounded-full mb-1 bg-gradient-to-t ${q.id === 1 ? 'from-red-500' : q.id === 2 ? 'from-blue-500' : q.id === 3 ? 'from-amber-500' : 'from-slate-500'} to-transparent opacity-30`}>
                    <div className="w-full bg-current rounded-full" style={{ height: `${(stats.quadrantCounts[i] / (stats.total || 1)) * 100}%` }}></div>
                  </div>
                  <span className="text-[10px] font-bold text-slate-400">Q{q.id}</span>
                </div>
              ))}
            </div>
            <button 
              onClick={clearCompleted}
              className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-red-500 hover:bg-red-50 rounded-xl transition-colors"
            >
              <Trash size={16} /> 완료 항목 삭제
            </button>
          </div>
        </section>

        {/* Input Form */}
        <form onSubmit={addTask} className="mb-10 group">
          <div className="bg-white p-2 pl-6 rounded-2xl border-2 border-slate-200 shadow-sm focus-within:border-indigo-500 transition-all flex items-center gap-4">
            <input
              type="text"
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              placeholder="새로운 작업 내용을 입력하세요..."
              className="flex-1 bg-transparent py-3 outline-none text-slate-700 font-medium"
            />
            <div className="hidden sm:flex items-center gap-2 border-l border-slate-200 pl-4 mr-2">
              <select 
                value={selectedQuadrant}
                onChange={(e) => setSelectedQuadrant(Number(e.target.value))}
                className="bg-slate-50 text-xs font-bold py-2 px-3 rounded-lg outline-none cursor-pointer text-slate-600"
              >
                {quadrants.map(q => <option key={q.id} value={q.id}>Q{q.id} - {q.label}</option>)}
              </select>
            </div>
            <button 
              type="submit"
              disabled={!newTask.trim()}
              className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 disabled:opacity-30 disabled:hover:bg-indigo-600 transition-all shadow-lg shadow-indigo-200"
            >
              <Plus size={20} strokeWidth={3} />
            </button>
          </div>
        </form>

        {activeTab === 'matrix' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {quadrants.map((q) => (
              <div key={q.id} className={`flex flex-col bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow`}>
                <div className={`p-5 flex items-center justify-between border-b border-slate-100 ${q.bgColor}`}>
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-xl bg-white shadow-sm ${q.textColor}`}>
                      {q.icon}
                    </div>
                    <div>
                      <h3 className={`font-black text-sm uppercase tracking-wider ${q.textColor}`}>{q.title}</h3>
                      <p className="text-slate-500 text-xs font-medium">{q.desc}</p>
                    </div>
                  </div>
                  <span className="text-2xl font-black opacity-10">{q.id}</span>
                </div>
                
                <div className="flex-1 p-4 space-y-3 min-h-[320px] max-h-[450px] overflow-y-auto">
                  {tasks.filter(t => t.quadrant === q.id).length === 0 ? (
                    <div className="h-full flex flex-row items-center justify-center opacity-30 gap-3 py-20">
                      <div className="text-sm font-medium italic">이 구역은 비어 있습니다.</div>
                    </div>
                  ) : (
                    tasks.filter(t => t.quadrant === q.id).map(task => (
                      <TaskItem 
                        key={task.id} 
                        task={task} 
                        toggleTask={toggleTask} 
                        deleteTask={deleteTask} 
                        moveTask={moveTask}
                        qStyle={q}
                      />
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6">
             <div className="space-y-4">
               {tasks.length === 0 ? (
                 <div className="py-20 text-center text-slate-400">등록된 할 일이 없습니다.</div>
               ) : (
                 tasks.map(task => (
                   <TaskItem 
                    key={task.id} 
                    task={task} 
                    toggleTask={toggleTask} 
                    deleteTask={deleteTask} 
                    moveTask={moveTask}
                    qStyle={quadrants.find(q => q.id === task.quadrant)}
                    showQuadrantLabel
                  />
                 ))
               )}
             </div>
          </div>
        )}
      </main>

      {/* Footer Info */}
      <footer className="max-w-6xl mx-auto px-6 mt-12 mb-8 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-full text-slate-500 text-[10px] font-bold uppercase tracking-widest">
          <Info size={12} /> 효율적인 시간 관리를 위한 아이젠하워 원칙
        </div>
      </footer>
    </div>
  );
};

const TaskItem = ({ task, toggleTask, deleteTask, moveTask, qStyle, showQuadrantLabel }) => (
  <div className={`group flex items-center gap-3 p-4 rounded-2xl border transition-all ${task.completed ? 'bg-slate-50 border-slate-100' : 'bg-white border-slate-100 hover:border-indigo-200 hover:shadow-sm'}`}>
    <button 
      onClick={() => toggleTask(task.id)}
      className={`flex-shrink-0 transition-all ${task.completed ? 'text-indigo-500 scale-110' : 'text-slate-300 hover:text-slate-400'}`}
    >
      {task.completed ? <CheckCircle2 size={22} fill="currentColor" className="text-white fill-indigo-500" /> : <Circle size={22} />}
    </button>
    
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2 mb-0.5">
        {showQuadrantLabel && (
          <span className={`text-[9px] font-black px-1.5 py-0.5 rounded uppercase ${qStyle.textColor} ${qStyle.bgColor} border ${qStyle.borderColor}`}>
            Q{task.quadrant}
          </span>
        )}
        <span className={`text-sm font-semibold truncate ${task.completed ? 'text-slate-400 line-through' : 'text-slate-700'}`}>
          {task.text}
        </span>
      </div>
    </div>

    <div className="flex items-center gap-1 sm:opacity-0 group-hover:opacity-100 transition-opacity">
      <button 
        onClick={() => moveTask(task.id)}
        className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-colors"
        title="다음 사분면으로 이동"
      >
        <ChevronRight size={18} />
      </button>
      <button 
        onClick={() => deleteTask(task.id)}
        className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors"
      >
        <Trash2 size={18} />
      </button>
    </div>
  </div>
);

export default App;
