import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LearnerProvider } from "../src/context/LearnerContext";
import DashboardPage from "../src/app/(learner)/dashboard/page";
import LessonPage from "../src/app/(learner)/lesson/page";
import DiagnosticPage from "../src/app/(learner)/diagnostic/page";
import { LearnerService } from "../src/lib/api/services";
import type { SubjectCode } from "../src/lib/api/types";

interface DashboardPanelProps {
  onStartLesson?: () => void;
  onStartDiag?: () => void;
}

interface LessonPanelProps {
  onComplete?: () => void;
  onBack?: () => void;
}

interface DiagnosticPanelProps {
  onComplete?: (subject: SubjectCode, mastery: number) => void;
  onBack?: () => void;
}

// Mock next/navigation
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  usePathname: () => "/dashboard",
  useSearchParams: () => new URLSearchParams("subject=MATH&topic=Fractions"),
}));

const serviceMocks = vi.hoisted(() => ({
  getMastery: vi.fn(),
  getGamificationProfile: vi.fn(),
  generateLesson: vi.fn(),
  markLessonComplete: vi.fn(),
  awardXP: vi.fn(),
}));

vi.mock("../src/lib/api/services", () => ({
  LearnerService: {
    getMastery: serviceMocks.getMastery,
    getGamificationProfile: serviceMocks.getGamificationProfile,
    generateLesson: serviceMocks.generateLesson,
    markLessonComplete: serviceMocks.markLessonComplete,
    awardXP: serviceMocks.awardXP,
  },
}));

// Mock the components used in pages to avoid massive dependency chain
vi.mock("../src/components/eduboost/FeaturePanels", () => {
  const DashboardPanel = ({ onStartLesson, onStartDiag }: DashboardPanelProps) => (
    <div>
      <button onClick={onStartLesson}>Start lesson</button>
      <button onClick={onStartDiag}>Open diagnostic</button>
    </div>
  );
  const LessonPanel = ({ onComplete, onBack }: LessonPanelProps) => (
    <div>
      <button onClick={onComplete}>Complete Lesson</button>
      <button onClick={onBack}>Back</button>
    </div>
  );
  return { __esModule: true, DashboardPanel, LessonPanel, default: { DashboardPanel, LessonPanel } };
});

vi.mock("../src/components/eduboost/InteractiveDiagnostic", () => {
  const InteractiveDiagnostic = ({ onComplete, onBack }: DiagnosticPanelProps) => (
    <div>
      <button onClick={() => onComplete?.("MATH", 80)}>Complete Diagnostic</button>
      <button onClick={onBack}>Back</button>
    </div>
  );
  return { __esModule: true, InteractiveDiagnostic, default: { InteractiveDiagnostic } };
});

vi.mock("../src/components/eduboost/InteractiveLesson", () => {
  const InteractiveLesson = ({ onComplete, onBack }: LessonPanelProps) => (
    <div>
      <button onClick={onComplete}>Complete Lesson</button>
      <button onClick={onBack}>Back</button>
    </div>
  );
  return { __esModule: true, default: InteractiveLesson };
});

describe("Routing Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    serviceMocks.getMastery.mockResolvedValue({
      learner_id: "learner-1",
      mastery: [{ subject_code: "MATH", mastery_score: 0.75 }],
    });
    serviceMocks.getGamificationProfile.mockResolvedValue({
      learner_id: "learner-1",
      total_xp: 80,
      level: 2,
      streak_days: 4,
      earned_badges: [],
    });
    serviceMocks.generateLesson.mockResolvedValue({
      id: "lesson-1",
      title: "Fractions",
      content: "A quick fractions lesson.",
      summary: "Fractions made friendly.",
    });
    serviceMocks.markLessonComplete.mockResolvedValue({ detail: "completed" });
    serviceMocks.awardXP.mockResolvedValue({
      awarded: true,
      xp_amount: 35,
      lesson_completed: true,
      profile: { learner_id: "learner-1", total_xp: 115, level: 2, streak_days: 4, earned_badges: [] },
    });
    window.localStorage.setItem(
      "eb_active_learner",
      JSON.stringify({
        learner_id: "learner-1",
        id: "learner-1",
        nickname: "Test Learner",
        grade: 3,
        avatar: 0,
      })
    );
  });

  it("Dashboard routes to /lesson and /diagnostic (NOT /learner/*)", async () => {
    render(
      <LearnerProvider>
        <DashboardPage />
      </LearnerProvider>
    );

    fireEvent.click(await screen.findByText("Start New Lesson"));
    expect(mockPush).toHaveBeenCalledWith("/lesson");

    fireEvent.click(screen.getByText("Take Assessment"));
    expect(mockPush).toHaveBeenCalledWith("/diagnostic");
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it("Lesson page completion routes back to /dashboard", async () => {
    render(
      <LearnerProvider>
        <LessonPage />
      </LearnerProvider>
    );

    fireEvent.click(await screen.findByText("Mathematics"));
    fireEvent.click(await screen.findByText("Fractions"));
    fireEvent.click(screen.getByText("Start Adventure"));

    fireEvent.click(await screen.findByText("Complete Lesson"));
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith("/dashboard"));
    expect(serviceMocks.markLessonComplete).toHaveBeenCalledWith("lesson-1");
    expect(serviceMocks.awardXP).toHaveBeenCalledWith(expect.objectContaining({ learner_id: "learner-1", xp_amount: 35 }));
    expect(mockPush).toHaveBeenCalledWith("/dashboard");
  });

  it("Diagnostic page routes to /plan and /dashboard", () => {
    render(
      <LearnerProvider>
        <DiagnosticPage />
      </LearnerProvider>
    );

    fireEvent.click(screen.getByText("Back"));
    expect(mockPush).toHaveBeenCalledWith("/dashboard");

    fireEvent.click(screen.getByText("Complete Diagnostic"));
    expect(mockPush).toHaveBeenCalledWith("/plan");
  });
});
