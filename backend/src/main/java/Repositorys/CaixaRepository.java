package Repositorys;

import Models.CaixaModel;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CaixaRepository extends JpaRepository<CaixaModel, Long> {
}