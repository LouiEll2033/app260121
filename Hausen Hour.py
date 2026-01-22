import React, { useState, useEffect, useRef } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { getFirestore, collection, addDoc, onSnapshot, doc, deleteDoc, updateDoc } from 'firebase/firestore';
import { 
  Plus, Trash2, CheckCircle2, Circle, AlertCircle, 
  Clock, Users, Trash, Calendar, ChevronLeft, 
  ChevronRight, GripVertical, Sparkles, X, Loader2
} from 'lucide-react';

// --- Firebase Configuration ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'eisenhower-matrix-v2';
const apiKey = ""; // Gemini API Key

const App = () => {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [taskInput, setTaskInput] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(true);
  
  // AI States
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [showAiModal, setShowAiModal] = useState(false);

  // 1. Authentication
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (error) {
        console.error("Auth error:", error);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      if (currentUser) setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  // 2. Data Fetching
  useEffect(() => {
    if (!user) return;
    const q = collection(db, 'artifacts', appId, 'users', user.uid, 'tasks');
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const taskList = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setTasks(taskList);
    }, (error) => {
      console.error("Firestore error:", error);
    });
    return () => unsubscribe();
  }, [user]);

  const visibleTasks = tasks.filter(task => {
    const isSameDate = task.date === selectedDate;
    const isPastUncompleted = task.date < selectedDate && !task.completed;
    return isSameDate || isPastUncompleted;
  });

  // --- Gemini API Call ---
  const callGemini = async (prompt, systemInstruction = "") => {
    const maxRetries = 5;
    let delay = 1000;
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            systemInstruction: systemInstruction ? { parts: [{ text: systemInstruction }] } : undefined
          })
        });
        if (!response.ok) throw new Error('API Request Failed');
        const data = await response.json();
        return data.candidates?.[0]?.content?.parts?.[0]?.text;
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, delay));
        delay *= 2;
      }
    }
  };

  const analyzeTaskWithAI = async (task) => {
    setAiLoading(true);
    setAiResponse(null);
    setShowAiModal(true);
    const quadrantText = {
      1: "중요하고 긴급한 일", 2: "중요하지만 긴급하지 않은 일",
      3: "긴급하지만 중요하지 않은 일", 4: "중요하지도 긴급하지도 않은 일"
    }[task.important ? (task.urgent ? 1 : 2) : (task.urgent ? 3 : 4)];

    try {
      const result = await callGemini(`"${task.text}" (${quadrantText}) 이 일의 효율적인 처리 방법을 조언해줘.`, "생산성 전문가로서 한국어로 친절하게 3~5줄 답변해줘.");
      setAiResponse(result);
    } catch (err) {
      setAiResponse("AI 분석 중 오류가 발생했습니다.");
    } finally {
      setAiLoading(false);
    }
  };

  const getDailyCoaching = async () => {
    if (visibleTasks.length === 0) return;
    setAiLoading(true);
    setAiResponse(null);
    setShowAiModal(true);
    const list = visibleTasks.map(t => `- [${t.important ? '중요' : '보통'}/${t.urgent ? '긴급' : '비긴급'}] ${t.text}`).join('\n');
    try {
      const result = await callGemini(`오늘의 할 일:\n${list}\n업무 전략을 짜줘.`, "시간 관리 전문가로서 한국어로 요약해줘.");
      setAiResponse(result);
    } catch (err) {
      setAiResponse("코칭을 가져오지 못했습니다.");
    } finally {
      setAiLoading(false);
    }
  };

  const addTaskToQuadrant = async (quadrantNum) => {
    if (!taskInput.trim() || !user) return;
    const config = {
      1: { urgent: true, important: true },
      2: { urgent: false, important: true },
      3: { urgent: true, important: false },
      4: { urgent: false, important: false }
    }[quadrantNum];

    try {
      await addDoc(collection(db, 'artifacts', appId, 'users', user.uid, 'tasks'), {
        text: taskInput,
        ...config,
        completed: false,
        date: selectedDate,
        createdAt: Date.now()
      });
      setTaskInput('');
    } catch (error) {
      console.error("Error adding task:", error);
    }
  };

  const toggleComplete = async (task) => {
    if (!user) return;
    await updateDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'tasks', task.id), { completed: !task.completed });
  };

  const deleteTask = async (id) => {
    if (!user) return;
    await deleteDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'tasks', id));
  };

  const onDragStart = (e, taskId) => e.dataTransfer.setData("taskId", taskId);
  const onDragOver = (e) => e.preventDefault();
  const onDrop = async (e, quadrantNum) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData("taskId");
    if (!user || !taskId) return;
    const config = {
      1: { urgent: true, important: true }, 2: { urgent: false, important: true },
      3: { urgent: true, important: false }, 4: { urgent: false, important: false }
    }[quadrantNum];
    await updateDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'tasks', taskId), config);
  };

  const changeDate = (days) => {
    const current = new Date(selectedDate);
    current.setDate(current.getDate() + days);
    setSelectedDate(current.toISOString().split('T')[0]);
  };

  // Color Mapping for Pastels
  const quadrantColors = {
    1: { border: 'border-rose-200', bg: 'bg-rose-50', icon: 'text-rose-500', btn: 'bg-rose-50 text-rose-600 border-rose-100 hover:bg-rose-500 hover:text-white hover:border-rose-500' },
    2: { border: 'border-emerald-200', bg: 'bg-emerald-50', icon: 'text-emerald-500', btn: 'bg-emerald-50 text-emerald-600 border-emerald-100 hover:bg-emerald-500 hover:text-white hover:border-emerald-500' },
    3: { border: 'border-sky-200', bg: 'bg-sky-50', icon: 'text-sky-500', btn: 'bg-sky-50 text-sky-600 border-sky-100 hover:bg-sky-500 hover:text-white hover:border-sky-500' },
    4: { border: 'border-violet-200', bg: 'bg-violet-50', icon: 'text-violet-500', btn: 'bg-violet-50 text-violet-600 border-violet-100 hover:bg-violet-500 hover:text-white hover:border-violet-500' }
  };

  const Quadrant = ({ num, title, urgent, important, icon: Icon }) => {
    const quadrantTasks = visibleTasks.filter(t => t.urgent === urgent && t.important === important);
    const styles = quadrantColors[num];
    return (
      <div 
        className={`flex flex-col h-full rounded-2xl border-2 p-2 ${styles.bg} ${styles.border} shadow-sm overflow-hidden relative transition-colors`}
        onDragOver={onDragOver}
        onDrop={(e) => onDrop(e, num)}
      >
        <div className="flex items-center gap-2 mb-2 shrink-0 px-1">
          <div className={`p-1 rounded-lg bg-white bg-opacity-60 shadow-sm`}>
            <Icon size={12} className={styles.icon} />
          </div>
          <h3 className="font-bold text-slate-700 text-[10px] sm:text-xs truncate">{num}. {title}</h3>
          <span className="ml-auto bg-white bg-opacity-60 text-slate-500 text-[9px] px-1.5 py-0.5 rounded-full font-bold">{quadrantTasks.length}</span>
        </div>
        <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
          {quadrantTasks.map(task => (
            <div 
              key={task.id} draggable onDragStart={(e) => onDragStart(e, task.id)}
              className={`group flex items-start gap-1.5 p-2 rounded-xl border border-white/50 bg-white/80 backdrop-blur-sm shadow-sm cursor-grab active:cursor-grabbing hover:border-indigo-200 transition-all ${task.date < selectedDate ? 'ring-1 ring-amber-200' : ''}`}
            >
              <button onClick={() => toggleComplete(task)} className="mt-0.5 shrink-0">
                {task.completed ? <CheckCircle2 size={14} className="text-green-500" /> : <Circle size={14} className="text-slate-200" />}
              </button>
              <div className="flex-1 min-w-0">
                <p className={`text-[11px] leading-tight break-words ${task.completed ? 'text-slate-300 line-through' : 'text-slate-700 font-medium'}`}>{task.text}</p>
                <button onClick={() => analyzeTaskWithAI(task)} className="text-[8px] text-indigo-500 hover:underline mt-1 font-bold">✨ AI 가이드</button>
              </div>
              <button onClick={() => deleteTask(task.id)} className="text-slate-200 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 size={12} /></button>
            </div>
          ))}
          {quadrantTasks.length === 0 && (
            <div className="h-full flex items-center justify-center text-slate-300 text-[9px] italic py-4">기록 없음</div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="h-screen bg-white font-sans text-slate-900 flex flex-col overflow-hidden relative">
      {/* AI Modal */}
      {showAiModal && (
        <div className="absolute inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="bg-white rounded-3xl w-full max-w-sm shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200 flex flex-col max-h-[80vh]">
            <div className="bg-indigo-600 px-5 py-4 flex justify-between items-center text-white shrink-0">
              <div className="flex items-center gap-2">
                <Sparkles size={18} />
                <h2 className="font-bold text-sm">AI 가이드</h2>
              </div>
              <button onClick={() => setShowAiModal(false)} className="hover:bg-white/20 p-1 rounded-full"><X size={18} /></button>
            </div>
            <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
              {aiLoading ? (
                <div className="flex flex-col items-center justify-center py-10 gap-3">
                  <Loader2 size={32} className="text-indigo-600 animate-spin" />
                  <p className="text-xs text-slate-500">분석 중...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap break-words italic">
                    {aiResponse}
                  </p>
                  <button onClick={() => setShowAiModal(false)} className="w-full py-3 bg-indigo-600 text-white rounded-xl text-xs font-bold">확인</button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <header className="bg-white border-b border-slate-100 px-4 py-3 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-2">
          <Calendar className="text-indigo-500" size={18} />
          <div className="flex items-center gap-1">
            <button onClick={() => changeDate(-1)} className="p-1"><ChevronLeft size={16}/></button>
            <span className="font-bold text-xs w-20 text-center">{selectedDate === new Date().toISOString().split('T')[0] ? '오늘' : selectedDate}</span>
            <button onClick={() => changeDate(1)} className="p-1"><ChevronRight size={16}/></button>
          </div>
        </div>
        <h1 className="font-bold text-sm text-slate-700">아우젠하워 매트릭스</h1>
        <button onClick={getDailyCoaching} className="text-[10px] font-bold text-white bg-indigo-500 px-4 py-1.5 rounded-full shadow-lg shadow-indigo-100">✨ 코칭</button>
      </header>

      <main className="flex-1 flex flex-col p-3 gap-3 overflow-hidden">
        <section className="bg-slate-50/50 p-3 rounded-2xl border border-slate-100 shrink-0">
          <div className="space-y-3">
            <div className="relative">
              <input
                type="text"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                placeholder="어떤 일을 기록할까요?"
                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-xs outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
              />
            </div>
            <div className="grid grid-cols-4 gap-2">
              {[1, 2, 3, 4].map(num => (
                <button
                  key={num}
                  onClick={() => addTaskToQuadrant(num)}
                  className={`py-2.5 rounded-xl text-[10px] font-black transition-all border-2 active:scale-95 shadow-sm ${quadrantColors[num].btn}`}
                >
                  {num}번 저장
                </button>
              ))}
            </div>
          </div>
        </section>

        <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-2 min-h-0 pb-2">
          <Quadrant num={1} title="중요/긴급" urgent={true} important={true} icon={AlertCircle} />
          <Quadrant num={2} title="중요/비긴급" urgent={false} important={true} icon={Clock} />
          <Quadrant num={3} title="긴급/비중요" urgent={true} important={false} icon={Users} />
          <Quadrant num={4} title="여유/보류" urgent={false} important={false} icon={Trash} />
        </div>
      </main>

      <style dangerouslySetInnerHTML={{ __html: `
        .custom-scrollbar::-webkit-scrollbar { width: 3px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
      `}} />
    </div>
  );
};

export default App;
