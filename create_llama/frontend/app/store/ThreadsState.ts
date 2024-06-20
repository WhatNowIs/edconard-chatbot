import create from 'zustand';

// Dummy data for threads
const dummyThreads = [
  { id: 1, title: 'Thread 1', content: 'This is thread 1' },
  { id: 2, title: 'Thread 2', content: 'This is thread 2' },
  { id: 3, title: 'Thread 3', content: 'This is thread 3' },
];

type Thread = {
  id: number;
  title: string;
  content: string;
};

type ThreadsState = {
  threads: Thread[];
  selectedThread: Thread | null;
  getThreads: () => void;
  getThread: (id: number) => Thread | undefined;
  createThread: (title: string, content: string) => void;
  selectThread: (id: number) => void;
};

export const useThreadsStore = create<ThreadsState>((set, get) => ({
  threads: dummyThreads,
  selectedThread: null,
  getThreads: () => {
    // Uncomment the following lines to fetch threads from an API
    // fetch('/api/threads')
    //   .then((res) => res.json())
    //   .then((data) => set({ threads: data }));

    // For now, we're using dummy data
    set({ threads: dummyThreads });
  },
  getThread: (id) => {
    // Uncomment the following lines to fetch a single thread from an API
    // fetch(`/api/threads/${id}`)
    //   .then((res) => res.json())
    //   .then((data) => set({ threads: [data] }));

    // For now, we're using dummy data
    return dummyThreads.find((thread) => thread.id === id);
  },
  createThread: (title, content) => {
    // Uncomment the following lines to create a thread through an API
    // fetch('/api/threads', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ title, content }),
    // })
    //   .then((res) => res.json())
    //   .then((data) => set((state) => ({ threads: [data, ...state.threads] })));

    // For now, we're just adding to the dummy data
    const newThread = { id: get().threads.length + 1, title, content };
    set((state) => ({ threads: [newThread, ...state.threads] }));
  },
  selectThread: (id) => {
    const thread = get().threads.find((thread) => thread.id === id);
    set({ selectedThread: thread || null });
  },
}));
