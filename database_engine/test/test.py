from sqlalchemy import create_engine,MetaData, Table
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.automap import automap_base


import os

#engine_definition = str("postgresql://fgeo:Polarcus123@127.0.0.1:1111/abhi_038916")
engine_definition = str("postgresql://fgeo:Polarcus123@127.0.0.1:1111/abhi_038916")
print "Now setting up DB engine .."
db_engine = create_engine(engine_definition, poolclass=QueuePool, echo=False)

metadata = MetaData( schema = "deliverables_qc")
Base_deliverables_qc = automap_base(metadata=metadata)
Base_deliverables_qc.prepare(db_engine, reflect=True)

s = scoped_session(sessionmaker(bind=db_engine))

Session = sessionmaker(db_engine)
sess = Session()

cmd = """
    SELECT l.sequence_number AS seq,
        l.real_line_name,
        l.preplot_name,
        a.first_ffid,
        a.first_shot,
        orca.ffid(l.sequence_number, e.fgsp) AS fg_ffid,
        e.fgsp,
        orca.ffid(l.sequence_number, e.lgsp) AS lg_ffid,
        e.lgsp,
        a.last_ffid,
        a.last_shot,
        to_char(l.start_time, 'DD-MM-YYYY'::text) AS start_data
       FROM orca.line l
         JOIN orca.edit_good_shot_point e USING (sequence_number)
         JOIN orca.all_sp a USING (sequence_number)
      ORDER BY l.sequence_number;
      """
result = s.execute(cmd)

# for a_item in result:
#     print a_item


Raw_seq_info = Base_deliverables_qc.classes.raw_seq_info
#
for seq_data in result:
    new_entry = Raw_seq_info()
    (new_entry.seq, new_entry.real_line_name, new_entry.preplot_name, new_entry.first_ffid, new_entry.first_shot,new_entry.fg_ffid, new_entry.fgsp, new_entry.lg_ffid, new_entry.lgsp, new_entry.last_ffid, new_entry.last_shot,new_entry.start_data) = seq_data
    old_object = sess.query(Raw_seq_info).filter(Raw_seq_info.seq == new_entry.seq).first()
    for a_key in new_entry.__dict__.keys():
        if a_key == '_sa_instance_state':
            pass
        else:
            if str(new_entry.__dict__[a_key]) == str(old_object.__dict__[a_key]):
                pass
            else:
                print str(new_entry.seq) + " : " + str(a_key) + " old: " + str(old_object.__dict__[a_key]) + " new: " + str(new_entry.__dict__[a_key])
                if new_entry.__dict__[a_key] != None:
                    setattr(old_object,a_key,str(new_entry.__dict__[a_key]))

                else:
                    print "Omit as the new entry is None"

sess.commit()









