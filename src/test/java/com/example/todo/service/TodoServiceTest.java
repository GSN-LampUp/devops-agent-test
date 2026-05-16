package com.example.todo.service;

import com.example.todo.model.Todo;
import com.example.todo.repository.TodoRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TodoServiceTest {

    @Mock
    private TodoRepository todoRepository;

    @InjectMocks
    private TodoService todoService;

    private Todo sampleTodo;

    @BeforeEach
    void setUp() {
        sampleTodo = new Todo(1L, "Sample", "Sample Description");
    }

    @Test
    void getAllTodos_returnsList() {
        when(todoRepository.findAll()).thenReturn(List.of(sampleTodo));

        List<Todo> result = todoService.getAllTodos();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getTitle()).isEqualTo("Sample");
    }

    @Test
    void getTodoById_found() {
        when(todoRepository.findById(1L)).thenReturn(Optional.of(sampleTodo));

        Optional<Todo> result = todoService.getTodoById(1L);

        assertThat(result).isPresent();
        assertThat(result.get().getTitle()).isEqualTo("Sample");
    }

    @Test
    void getTodoById_notFound() {
        when(todoRepository.findById(99L)).thenReturn(Optional.empty());

        Optional<Todo> result = todoService.getTodoById(99L);

        assertThat(result).isEmpty();
    }

    @Test
    void createTodo_setsDefaults() {
        when(todoRepository.save(any(Todo.class))).thenAnswer(inv -> {
            Todo t = inv.getArgument(0);
            t.setId(1L);
            return t;
        });

        Todo input = new Todo(null, "New", "Desc");
        Todo result = todoService.createTodo(input);

        assertThat(result.isCompleted()).isFalse();
        assertThat(result.getCreatedAt()).isNotNull();
        assertThat(result.getUpdatedAt()).isNotNull();
    }

    @Test
    void updateTodo_found() {
        when(todoRepository.findById(1L)).thenReturn(Optional.of(sampleTodo));
        when(todoRepository.save(any(Todo.class))).thenAnswer(inv -> inv.getArgument(0));

        Todo updated = new Todo(null, "Updated", "Updated Desc");
        updated.setCompleted(true);

        Optional<Todo> result = todoService.updateTodo(1L, updated);

        assertThat(result).isPresent();
        assertThat(result.get().getTitle()).isEqualTo("Updated");
        assertThat(result.get().isCompleted()).isTrue();
    }

    @Test
    void updateTodo_notFound() {
        when(todoRepository.findById(99L)).thenReturn(Optional.empty());

        Optional<Todo> result = todoService.updateTodo(99L, new Todo());

        assertThat(result).isEmpty();
    }

    @Test
    void deleteTodo_exists() {
        when(todoRepository.existsById(1L)).thenReturn(true);

        boolean result = todoService.deleteTodo(1L);

        assertThat(result).isTrue();
        verify(todoRepository).deleteById(1L);
    }

    @Test
    void deleteTodo_notExists() {
        when(todoRepository.existsById(99L)).thenReturn(false);

        boolean result = todoService.deleteTodo(99L);

        assertThat(result).isFalse();
        verify(todoRepository, never()).deleteById(any());
    }
}
