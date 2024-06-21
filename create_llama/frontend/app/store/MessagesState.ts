// import create from 'zustand';

// // Dummy data for messages
// const dummyMessages = [
//   { id: '1', thread_id: '1', sender: 'human', content: 'This is message 1', timestamp: new Date() },
//   { id: '2', thread_id: '1', sender: 'assistant', content: 'This is message 2', timestamp: new Date() },
//   { id: '3', thread_id: '1', sender: 'human', content: 'This is message 3', timestamp: new Date() },
// ];

// type Message = {
//   id: string;
//   thread_id: string;
//   sender: string;
//   content: string;
//   timestamp: Date;
// };

// type MessagesState = {
//   messages: Message[];
//   createMessage: (thread_id: string, sender: string, content: string) => void;
//   deleteMessage: (id: string) => void;
// };

// export const useMessagesStore = create<MessagesState>((set) => ({
//   messages: dummyMessages,
//   createMessage: (thread_id, sender, content) => {
//     // Uncomment the following lines to create a message through an API
//     // fetch('/api/messages', {
//     //   method: 'POST',
//     //   headers: { 'Content-Type': 'application/json' },
//     //   body: JSON.stringify({ thread_id, sender, content }),
//     // })
//     //   .then((res) => res.json())
//     //   .then((data) => set((state) => ({ messages: [...state.messages, data] })));

//     // For now, we're just adding to the dummy data
//     const newMessage = { id: (dummyMessages.length + 1).toString(), thread_id, sender, content, timestamp: new Date() };
//     set((state) => ({ messages: [...state.messages, newMessage] }));
//   },
//   deleteMessage: (id) => {
//     // Uncomment the following lines to delete a message through an API
//     // fetch(`/api/messages/${id}`, {
//     //   method: 'DELETE',
//     // })
//     //   .then(() => set((state) => ({ messages: state.messages.filter((message) => message.id !== id) })));

//     // For now, we're just removing from the dummy data
//     set((state) => ({ messages: state.messages.filter((message) => message.id !== id) }));
//   },
// }));
