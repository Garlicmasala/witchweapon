"""
Visual Novel Interlude System for Witch's Weapon PvE.
Handles story nodes, dialogue flow, optional choices, versioning, and map-triggered interludes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class DialogueLine:
    speaker: str
    text: str
    emotion_tag: str = "neutral"
    voice_line: Optional[str] = None
    illustration_tag: Optional[str] = None


@dataclass
class ChoiceOption:
    text: str
    next_node_id: str
    flags_set: Dict[str, Any] = field(default_factory=dict)
    affection_delta: Dict[str, int] = field(default_factory=dict)


@dataclass
class StoryNode:
    node_id: str
    version: str
    valid_from_patch: str
    retired: bool = False
    illustration: Optional[str] = None
    illustration_type: Optional[str] = None
    dialogue_lines: List[DialogueLine] = field(default_factory=list)
    choices: List[ChoiceOption] = field(default_factory=list)
    flags_required: Dict[str, Any] = field(default_factory=dict)
    flags_set: Dict[str, Any] = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)
    unlock_condition: Optional[Dict[str, Any]] = None

    def is_valid_for_flags(self, flags: Dict[str, Any]) -> bool:
        for key, value in self.flags_required.items():
            if flags.get(key) != value:
                return False
        return True

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "version": self.version,
            "valid_from_patch": self.valid_from_patch,
            "retired": self.retired,
            "illustration": self.illustration,
            "illustration_type": self.illustration_type,
            "dialogue_lines": [dl.__dict__ for dl in self.dialogue_lines],
            "choices": [c.__dict__ for c in self.choices],
            "flags_required": self.flags_required,
            "flags_set": self.flags_set,
            "next_nodes": self.next_nodes,
            "unlock_condition": self.unlock_condition,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "StoryNode":
        dialogue_lines = [DialogueLine(**line) for line in data.get("dialogue_lines", [])]
        choices = [ChoiceOption(**choice) for choice in data.get("choices", [])]
        return cls(
            node_id=data["node_id"],
            version=data.get("version", "1.0.0"),
            valid_from_patch=data.get("valid_from_patch", "1.0.0"),
            retired=data.get("retired", False),
            illustration=data.get("illustration"),
            illustration_type=data.get("illustration_type"),
            dialogue_lines=dialogue_lines,
            choices=choices,
            flags_required=data.get("flags_required", {}),
            flags_set=data.get("flags_set", {}),
            next_nodes=data.get("next_nodes", []),
            unlock_condition=data.get("unlock_condition"),
        )


@dataclass
class StoryArc:
    arc_id: str
    title: str
    chapter_node_ids: List[str] = field(default_factory=list)
    insert_points: List[str] = field(default_factory=list)
    resolution_placeholder: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "arc_id": self.arc_id,
            "title": self.title,
            "chapter_node_ids": self.chapter_node_ids,
            "insert_points": self.insert_points,
            "resolution_placeholder": self.resolution_placeholder,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "StoryArc":
        return cls(
            arc_id=data["arc_id"],
            title=data["title"],
            chapter_node_ids=data.get("chapter_node_ids", []),
            insert_points=data.get("insert_points", []),
            resolution_placeholder=data.get("resolution_placeholder"),
        )


class VisualNovelManager:
    def __init__(self, ui_feedback, patch_version: str = "1.0.0", daily_mission_manager=None):
        self.ui = ui_feedback
        self.daily_mission_manager = daily_mission_manager
        self.story_graph: Dict[str, StoryNode] = {}
        self.arcs: Dict[str, StoryArc] = {}
        self.flags: Dict[str, Any] = {}
        self.current_node_id: Optional[str] = None
        self.pending_nodes: List[str] = []
        self.archive: List[str] = []
        self.patch_version = patch_version
        self.version_history: List[str] = [patch_version]

    def load_story_graph(self, graph_data: Dict[str, Any]):
        nodes = graph_data.get("nodes", [])
        for node_data in nodes:
            node = StoryNode.from_dict(node_data)
            self.story_graph[node.node_id] = node
        arcs = graph_data.get("arcs", [])
        for arc_data in arcs:
            arc = StoryArc.from_dict(arc_data)
            self.arcs[arc.arc_id] = arc

    def queue_story_node(self, node_id: str):
        node = self.story_graph.get(node_id)
        if not node or node.retired:
            return False
        if not node.is_valid_for_flags(self.flags):
            return False
        if node_id in self.pending_nodes or node_id in self.archive:
            return False
        self.pending_nodes.append(node_id)
        self.ui.display_message(f"[VisualNovel] Story node queued: {node_id}")
        return True

    def has_pending_story(self) -> bool:
        return len(self.pending_nodes) > 0

    def play_next_interlude(self):
        if not self.pending_nodes:
            return False
        self.current_node_id = self.pending_nodes.pop(0)
        node = self.story_graph.get(self.current_node_id)
        if not node:
            return False
        self._play_node(node)
        self.archive.append(node.node_id)
        self.current_node_id = None
        return True

    def _play_node(self, node: StoryNode):
        self.ui.display_message(f"=== Visual Novel Interlude: {node.node_id} ===")
        if node.illustration:
            self.ui.display_message(f"[Illustration: {node.illustration} / {node.illustration_type}]")
        for line in node.dialogue_lines:
            prefix = f"{line.speaker} [{line.emotion_tag}]" if line.emotion_tag else line.speaker
            self.ui.display_message(f"{prefix}: {line.text}")
            if line.voice_line:
                self.ui.display_message(f"[Voice line: {line.voice_line}]")
        self._set_flags(node.flags_set)
        if self.daily_mission_manager:
            self.daily_mission_manager.on_vn_node_read()
        if node.choices:
            self._present_choices(node)
        else:
            self._advance_to_next(node)

    def _present_choices(self, node: StoryNode):
        self.ui.display_message("--- Make a choice ---")
        for index, choice in enumerate(node.choices, start=1):
            self.ui.display_message(f"{index}. {choice.text}")
        self.ui.display_message("0. Skip choice")
        while True:
            selection = input("Choose an option: ").strip()
            if selection.isdigit():
                choice_index = int(selection)
                if choice_index == 0:
                    self._advance_to_next(node)
                    return
                if 1 <= choice_index <= len(node.choices):
                    chosen = node.choices[choice_index - 1]
                    self._set_flags(chosen.flags_set)
                    for char, amount in chosen.affection_delta.items():
                        self.flags[f"affection_{char}"] = self.flags.get(f"affection_{char}", 0) + amount
                    self._queue_next_nodes([chosen.next_node_id])
                    self.play_next_interlude()
                    return
            self.ui.display_message("Invalid choice. Enter the number of your selection.")

    def _advance_to_next(self, node: StoryNode):
        self._queue_next_nodes(node.next_nodes)
        # Use immediate continuation if no additional node is queued by choice.
        if self.pending_nodes:
            self.play_next_interlude()

    def _queue_next_nodes(self, node_ids: List[str]):
        for next_id in node_ids:
            self.queue_story_node(next_id)

    def _set_flags(self, flags: Dict[str, Any]):
        for key, value in flags.items():
            self.flags[key] = value

    def get_state(self) -> Dict[str, Any]:
        return {
            "flags": self.flags,
            "current_node_id": self.current_node_id,
            "pending_nodes": list(self.pending_nodes),
            "archive": list(self.archive),
            "patch_version": self.patch_version,
            "version_history": list(self.version_history),
        }

    def load_state(self, state: Dict[str, Any]):
        self.flags = state.get("flags", {})
        self.current_node_id = state.get("current_node_id")
        self.pending_nodes = state.get("pending_nodes", [])
        self.archive = state.get("archive", [])
        self.patch_version = state.get("patch_version", self.patch_version)
        self.version_history = state.get("version_history", self.version_history)

    def get_archive(self) -> List[str]:
        return list(self.archive)

    def get_available_arcs(self) -> List[str]:
        return list(self.arcs.keys())

    def get_arc_overview(self, arc_id: str) -> Optional[Dict[str, Any]]:
        arc = self.arcs.get(arc_id)
        if not arc:
            return None
        return arc.to_dict()

    @staticmethod
    def create_default_story_graph() -> Dict[str, Any]:
        return {
            "nodes": [
                {
                    "node_id": "interlude_1",
                    "version": "1.0.0",
                    "valid_from_patch": "1.0.0",
                    "retired": False,
                    "illustration": "campfire_scene",
                    "illustration_type": "Half-body Portrait",
                    "dialogue_lines": [
                        {"speaker": "Narrator", "text": "After the fight, the heroes gather around the campfire.", "emotion_tag": "serene"},
                        {"speaker": "Companion", "text": "We almost lost them back there. Are you okay?", "emotion_tag": "concerned"}
                    ],
                    "choices": [
                        {"text": "Reassure them.", "next_node_id": "interlude_1a", "flags_set": {"trust_high": True}, "affection_delta": {"Companion": 10}},
                        {"text": "Change the subject.", "next_node_id": "interlude_1b", "flags_set": {"trust_high": False}, "affection_delta": {"Companion": 2}}
                    ],
                    "flags_required": {},
                    "flags_set": {"completed_interlude_1": True},
                    "next_nodes": []
                },
                {
                    "node_id": "interlude_1a",
                    "version": "1.0.0",
                    "valid_from_patch": "1.0.0",
                    "illustration": "companion_smile",
                    "illustration_type": "Half-body Portrait",
                    "dialogue_lines": [
                        {"speaker": "Companion", "text": "That's good to hear. We'll get through this together.", "emotion_tag": "warm"}
                    ],
                    "choices": [],
                    "flags_required": {},
                    "flags_set": {"shared_confidence": True},
                    "next_nodes": ["interlude_2"]
                },
                {
                    "node_id": "interlude_1b",
                    "version": "1.0.0",
                    "valid_from_patch": "1.0.0",
                    "illustration": "companion_thoughtful",
                    "illustration_type": "Half-body Portrait",
                    "dialogue_lines": [
                        {"speaker": "Companion", "text": "...If you're sure. Let me know if you need anything.", "emotion_tag": "quiet"}
                    ],
                    "choices": [],
                    "flags_required": {},
                    "flags_set": {},
                    "next_nodes": ["interlude_2"]
                },
                {
                    "node_id": "interlude_2",
                    "version": "1.0.0",
                    "valid_from_patch": "1.0.0",
                    "illustration": "moonlit_forest",
                    "illustration_type": "Environmental Art",
                    "dialogue_lines": [
                        {"speaker": "Narrator", "text": "A new path opens as the night deepens.", "emotion_tag": "mysterious"}
                    ],
                    "choices": [],
                    "flags_required": {},
                    "flags_set": {"completed_interlude_2": True},
                    "next_nodes": []
                }
            ],
            "arcs": [
                {
                    "arc_id": "arc_1",
                    "title": "Chapter One: Ember Stories",
                    "chapter_node_ids": ["interlude_1", "interlude_1a", "interlude_1b", "interlude_2"],
                    "insert_points": ["interlude_2"],
                    "resolution_placeholder": "Chapter One continuing..."
                }
            ]
        }
