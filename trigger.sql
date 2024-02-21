create or replace function inc_trigger() returns trigger
as $$
begin 
	
	delete from incoming i where old.id = i.cont_id;
	
return new;
end;
$$ language plpgsql;
CREATE  or replace TRIGGER int_trigger
BEFORE DELETE ON contracts
    FOR EACH ROW EXECUTE FUNCTION inc_trigger();
--триггер реализующий удаление всех записей связанных с контрактом из таблицы incoming