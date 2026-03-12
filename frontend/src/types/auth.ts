/**
 * 인증 관련 타입
 */

export interface User {
  id: string;
  email: string;
  name?: string;
  role: string;
}

export interface Organization {
  id: string;
  name: string;
}

export interface MemberContext {
  user: User;
  organization: Organization;
  role: string;
  plan: string;
}
