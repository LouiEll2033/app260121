import React, { useState, useEffect, useMemo } from 'react';
import { 
  Plus, Trash2, ChevronRight, CheckCircle2, 
  Circle, AlertCircle, Clock, Users, 
  XOctagon, LayoutGrid, ListTodo, Trash,
  Info, Edit, Save, X
} from 'lucide-react';

const App = () => {
  // 로컬 저장소 접근 시 발생할 수 있는 오류 방지를 위한 안전한 함수
  const getStoredTasks = () => {
    try {
      const saved = localStorage.getItem('eisenhower_tasks_v3');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.warn("저장소 접근 제한됨:", e);
    }
    return [
      { id: 1, text: '급한 프로젝트 보고서 작성', quadrant: 1, completed: false, createdAt: Date.now() },
      { id: 2, text: '자기계발 및 독서', quadrant: 2, completed: false, createdAt: Date.now() },
      { id: 3, text: '단순 반복 업무 메일 정리', quadrant: 3, completed: false, createdAt: Date.now() },
      { id: 4, text: '불필요한 웹서핑 줄이기', quadrant: 4, completed: false, createdAt: Date.now() },
    ];
  };

  const [tasks, setTasks] = useState(getStoredTasks);
  const [newTask, setNewTask] = useState('');
  const [selectedQuadrant, setSelectedQuadrant] = useState(1);
  const [activeTab, setActiveTab] = useState('matrix'); 
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  // 상태 변경 시 안전하게 저장
  useEffect(() => {
    try {
      localStorage.setItem('eisenhower_tasks_v3', JSON.stringify(tasks));
    } catch (e) {
      // 저장 실패 무시
    }
  }, [tasks]);

  const quadrants = [
    { 
      id: 1, 
      title: 'Do First', 
      label: '긴급 & 중요',
      desc: '지금 바로 처리하세요',
      color: 'from-rose-500 to-red-600', 
      bgColor: 'bg-rose-50',
      textColor: 'text-rose-700',
      borderColor: 'border-rose-200',
      icon: <AlertCircle size={20} />
    },
    { 
      id: 2, 
      title: 'Schedule', 
      label: '중요하나 안 긴급',
      desc: '수행 시간을 계획하세요',
      color: 'from-emerald-500 to-teal-600', 
      bgColor: 'bg-emerald-50',
      textColor: 'text-emerald-700',
      borderColor: 'border-emerald-200',
      icon: <Clock size={20} />
    },
    { 
      id: 3, 
      title: 'Delegate', 
      label: '긴급하나 안 중요',
      desc: '다른 사람에게 맡기세요',
      color: 'from-amber-400 to-orange-500', 
      bgColor: 'bg-amber-50',
      textColor: 'text-amber-700',
      borderColor: 'border-amber-200',
      icon: <Users size={20} />
    },
    { 
      id: 4, 
      title: 'Eliminate', 
      label: '둘 다 아님',
      desc: '과감히 삭제하세요',
      color: 'from-slate-500 to-slate-700', 
      bgColor: 'bg-slate-100',
      textColor: 'text-slate-700',
      borderColor: 'border-slate-200',
      icon: <XOctagon size={20} />
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
    const totalCount = tasks.length;
    const completedCount = tasks.filter(t => t.completed).length;
    const percentage = totalCount > 0 ? Math.floor((completedCount * 100) / totalCount) : 0;
    return { totalCount, completedCount, percentage };
  }, [tasks]);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 pb-24 font-sans">
      {/* 상단 네비게이션 */}
      <nav className="sticky top-0 z-40 bg-white border-b border-slate-200 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white">
              <LayoutGrid size={22} />
            </div>
            <h1 className="text-xl font-bold text-slate-800">Eisenhower Matrix</h1>
          </div>
          <div className="flex bg-slate-100 p-1 rounded-xl">
            <button 
              onClick={() => setActiveTab('matrix')}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'matrix' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}
            >
              매트릭스
            </button>
            <button 
              onClick={() => setActiveTab('list')}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'list' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`}
            >
              리스트
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-10">
        {/* 할 일 입력 섹션 */}
        <div className="max-w-3xl mx-auto mb-12">
          <form onSubmit={addTask} className="flex gap-4 bg-white p-2 pl-6 rounded-2xl border-2 border-slate-200 shadow-md focus-within:border-indigo-500">
            <input
              type="text"
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              placeholder="무엇을 계획 중인가요?"
              className="flex-1 bg-transparent py-3 outline-none font-bold"
            />
            <select 
              value={selectedQuadrant}
              onChange={(e) => setSelectedQuadrant(Number(e.target.value))}
              className="hidden sm:block bg-slate-50 text-xs font-bold outline-none cursor-pointer px-3 rounded-xl"
            >
              {quadrants.map(q => <option key={q.id} value={q.id}>Q{q.id} - {q.label}</option>)}
            </select>
            <button 
              type="submit"
              disabled={!newTask.trim()}
              className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 disabled:opacity-30"
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
                    <div className="w-12 h-12 rounded-xl bg-white shadow-sm flex items-center justify-center text-indigo-600">
                      {q.icon}
                    </div>
                    <div>
                      <h3 className={`font-bold text-lg ${q.textColor}`}>{q.title}</h3>
                      <p className="text-slate-500 text-xs font-semibold">{q.label}</p>
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
          <div className="bg-white rounded-3xl border border-slate-200 shadow-lg p-8 space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">전체 리스트</h2>
              <button onClick={clearCompleted} className="text-xs font-bold text-rose-500 hover:bg-rose-50 px-3 py-1.5 rounded-lg border border-rose-100">
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

        {/* 하단 통계 바 */}
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-8 py-4 rounded-full shadow-2xl flex items-center gap-8 z-50">
          <div className="flex flex-col text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Total</span>
            <span className="text-xl font-bold">{stats.totalCount}</span>
          </div>
          <div className="w-px h-8 bg-slate-700"></div>
          <div className="flex flex-col text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Progress</span>
            <span className="text-xl font-bold text-indigo-400">{stats.percentage}%</span>
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
    <div className={`group flex items-center gap-4 p-4 rounded-2xl border-2 transition-all ${task.completed ? 'bg-slate-50 border-slate-100 opacity-50' : 'bg-white border-slate-50 shadow-sm hover:border-indigo-100'}`}>
      <button onClick={() => toggleTask(task.id)} className={`flex-shrink-0 transition-transform hover:scale-110 ${task.completed ? 'text-indigo-500' : 'text-slate-200'}`}>
        {task.completed ? <CheckCircle2 size={24} fill="currentColor" className="text-white" /> : <Circle size={24} />}
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
            {showQuadrantLabel && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 border border-slate-200">{qLabel}</span>}
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
