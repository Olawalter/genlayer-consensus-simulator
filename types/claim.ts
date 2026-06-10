export interface Claim {
  id: string;
  userId: string | null;
  content: string;
  category: 'freelance' | 'review' | 'event' | 'custom';
  createdAt: string;
}
