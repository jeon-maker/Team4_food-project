package com.choi.dietdiaryapp.fragments;

import android.content.Intent;
import android.database.sqlite.SQLiteException;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v4.app.ShareCompat;
import android.support.v7.widget.DividerItemDecoration;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.choi.dietdiaryapp.BuildConfig;
import com.choi.dietdiaryapp.CreateEditEventActivity;
import com.choi.dietdiaryapp.MainActivity;
import com.choi.dietdiaryapp.R;
import com.choi.dietdiaryapp.db.DatabaseHelper;
import com.choi.dietdiaryapp.db.EventHelper;
import com.choi.dietdiaryapp.helpers.DateTimeHelper;
import com.choi.dietdiaryapp.models.Event;
import com.crashlytics.android.Crashlytics;

import org.joda.time.LocalDate;
import org.joda.time.format.DateTimeFormat;

import java.text.MessageFormat;
import java.util.ArrayList;

public class DayFragment extends Fragment {
    private static final String TAG = "DayFragment";
    private static final String KEY_DATE_SERIALIZABLE = "DATE";
    private static final String KEY_DATA_SET_PARCELABLE = "DATA SET";
    private static final String KEY_RELOAD_BOOLEAN = "RELOAD";

    private LocalDate mDate;
    private EventModelAdapter mAdapter;
    private ArrayList<Event> mSavedList;

    public static DayFragment newInstance(LocalDate date) {
        Log.d(TAG, "newInstance " + date);
        DayFragment fragment = new DayFragment();
        Bundle args = new Bundle();
        args.putSerializable(DayFragment.KEY_DATE_SERIALIZABLE, date);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setHasOptionsMenu(true);

        if (null != savedInstanceState) {
            mDate = (LocalDate) savedInstanceState.getSerializable(KEY_DATE_SERIALIZABLE);
            mSavedList = savedInstanceState.getParcelableArrayList(KEY_DATA_SET_PARCELABLE);
        } else {
            mDate = (LocalDate) getArguments().getSerializable(KEY_DATE_SERIALIZABLE);
            mSavedList = null;
        }

        Log.d(TAG, "onCreate " + mDate);
    }

    @Override
    public void onResume() {
        super.onResume();

        if (null != mAdapter) {
            mAdapter.refreshIfTimeFormatChanged(DateTimeHelper.is24HourMode(getContext()));
        }

        Log.d(TAG, "onResume " + mDate);
    }

    @Override
    public void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        Log.d(TAG, "onSaveInstanceState " + mDate);

        outState.putSerializable(KEY_DATE_SERIALIZABLE, mDate);

        if (null != mAdapter) {
            outState.putParcelableArrayList(KEY_DATA_SET_PARCELABLE, mAdapter.getDataSet());
        } else if (null != mSavedList) {
            outState.putParcelableArrayList(KEY_DATA_SET_PARCELABLE, mSavedList);
        }
    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
        inflater.inflate(R.menu.menu_day_fragment, menu);
        super.onCreateOptionsMenu(menu, inflater);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.action_share:
                if (null != mAdapter) {
                    if (0 == mAdapter.getItemCount()) {
                        Toast.makeText(getContext(), R.string.day_fragment_nothing_to_share, Toast.LENGTH_SHORT).show();
                        return true;
                    }

                    StringBuilder sb = new StringBuilder(getString(R.string.app_name));
                    sb.append(" - ").append(mDate.toString(DateTimeFormat.longDate())).append('\n');

                    for (Event e : mAdapter.getDataSet()) {
                        sb.append(getEventText(e));
                        sb.append('\n');
                    }

                    ShareCompat.IntentBuilder builder = ShareCompat.IntentBuilder.from(getActivity())
                            .setType("text/plain")
                            .setText(sb.toString());

                    builder.startChooser();
                }
                return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private String getEventText(final Event event) {
        StringBuilder sb = new StringBuilder();
        String[] types = getResources().getStringArray(R.array.spinner_event_types);
        String[] foodTypes = getResources().getStringArray(R.array.spinner_event_food_types);
        String[] drinkTypes = getResources().getStringArray(R.array.spinner_event_drink_types);

        switch (event.getType()) {
            case Event.TYPE_FOOD:
                sb.append(foodTypes[event.getSubType()]);
                break;
            case Event.TYPE_DRINK:
                sb.append(drinkTypes[event.getSubType()]);
                break;
            default:
                sb.append(types[event.getType()]);
                break;
        }

        sb.append(" (").append(event.getTime().toString(DatabaseHelper.DB_TIME_FORMATTER)).append("): ");
        sb.append(event.getDescription());

        return sb.toString();
    }

    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        Log.d(TAG, "onCreateView " + mDate);

        mAdapter = new EventModelAdapter(DateTimeHelper.is24HourMode(getContext()));

        if (null == mSavedList) {
            mAdapter.setDataSet(loadItems(mDate));
        } else {
            if (getArguments().getBoolean(KEY_RELOAD_BOOLEAN)) {
                mSavedList = loadItems(mDate);
                getArguments().remove(KEY_RELOAD_BOOLEAN);
            }

            mAdapter.setDataSet(mSavedList);
            mSavedList = null;
        }

        RecyclerView mRecyclerView = (RecyclerView) inflater.inflate(R.layout.fragment_day_recyclerview, container, false);
        mRecyclerView.addItemDecoration(new DividerItemDecoration(inflater.getContext(), DividerItemDecoration.VERTICAL));
        mRecyclerView.setLayoutManager(new LinearLayoutManager(inflater.getContext()));
        mRecyclerView.setAdapter(mAdapter);
        return mRecyclerView;
    }

    private ArrayList<Event> loadItems(@NonNull LocalDate date) {
        ArrayList<Event> list = null;
        try {
            list = EventHelper.getEventByDate(getContext(), date);
        } catch (SQLiteException e) {
            if (BuildConfig.CRASHLYTICS_ENABLED) {
                Crashlytics.logException(e);
            }
            Log.e(TAG, "Content cannot be prepared probably a DB issue.", e);
        }

        return list;
    }

    public void addNewEvent(Event newEvent) {
        if (null != mAdapter) {
            if (BuildConfig.CRASHLYTICS_ENABLED) {
                Crashlytics.log("Adding an event");
            }
            mAdapter.addNewEvent(newEvent);
        } else {
            getArguments().putBoolean(KEY_RELOAD_BOOLEAN, true);
        }
    }

    public void updateAnEventAt(Event updatedEvent, int position) {
        if (null != mAdapter) {
            if (BuildConfig.CRASHLYTICS_ENABLED) {
                Crashlytics.log("Updating an event at " + position);
            }
            mAdapter.updateAnEventAt(updatedEvent, position);
        } else {
            getArguments().putBoolean(KEY_RELOAD_BOOLEAN, true);
        }
    }

    public void deleteAnEventAt(Event deletedEvent, int position) {
        if (null != mAdapter) {
            if (BuildConfig.CRASHLYTICS_ENABLED) {
                Crashlytics.log("Deleting an event at " + position);
            }
            mAdapter.deleteAnEventAt(deletedEvent, position);
        } else {
            getArguments().putBoolean(KEY_RELOAD_BOOLEAN, true);
        }
    }

    interface OnItemClickListener {
        void onClick(View view, int position);
    }

    class EventModelAdapter extends RecyclerView.Adapter<EventModelAdapter.ViewHolder>
            implements OnItemClickListener {
        private static final String TAG = "EventModelAdapter";
        private boolean mIs24HourFormat;
        private ArrayList<Event> mList;

        EventModelAdapter(final boolean is24HourFormat) {
            mIs24HourFormat = is24HourFormat;
            mList = null;
        }

        @Override
        public EventModelAdapter.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
            View v = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.fragment_day_recyclerview_item, parent, false);

            return new EventModelAdapter.ViewHolder(this, v);
        }

        @Override
        public void onBindViewHolder(EventModelAdapter.ViewHolder holder, int position) {
            String[] arr = holder.itemView.getContext().getResources().getStringArray(R.array.spinner_event_types);
            Event model = mList.get(position);
            switch (model.getType()) {
                case Event.TYPE_FOOD:
                    arr = holder.itemView.getContext().getResources().getStringArray(R.array.spinner_event_food_types);
                    holder.tvTitle.setText(arr[model.getSubType()]);
                    break;
                case Event.TYPE_DRINK:
                    arr = holder.itemView.getContext().getResources().getStringArray(R.array.spinner_event_drink_types);
                    holder.tvTitle.setText(arr[model.getSubType()]);
                    break;
                default:
                    holder.tvTitle.setText(arr[model.getType()]);
                    break;
            }

            holder.tvDescription.setText(model.getDescription());
            holder.tvTime.setText(DateTimeHelper.convertLocalTimeToString(mIs24HourFormat, model.getTime()));

            switch (model.getType()) {
                case Event.TYPE_FOOD:
                    holder.ivIcon.setImageResource(R.drawable.food);
                    break;
                case Event.TYPE_DRINK:
                    holder.ivIcon.setImageResource(R.drawable.drink);
                    break;
                case Event.TYPE_MED:
                    holder.ivIcon.setImageResource(R.drawable.medication);
                    break;
                case Event.TYPE_SUPP:
                    holder.ivIcon.setImageResource(R.drawable.supplement);
                    break;
                case Event.TYPE_EXC:
                    holder.ivIcon.setImageResource(R.drawable.exercise);
                    break;
                case Event.TYPE_OTHER:
                default:
                    holder.ivIcon.setImageResource(R.drawable.other);
                    break;
            }
        }

        @Override
        public int getItemCount() {
            return mList == null ? 0 : mList.size();
        }

        @Override
        public void onClick(View view, int position) {
            Event event = mList.get(position);
            Intent intent = new Intent(view.getContext(), CreateEditEventActivity.class)
                    .putExtra(CreateEditEventActivity.KEY_EVENT_PARCELABLE, event)
                    .putExtra(CreateEditEventActivity.KEY_POSITION_INT, position);

            ((MainActivity) view.getContext()).startActivityForResult(intent, CreateEditEventActivity.REQUEST_CREATE_EDIT);
        }

        ArrayList<Event> getDataSet() {
            return mList;
        }

        void setDataSet(ArrayList<Event> list) {
            mList = list;

            notifyDataSetChanged();
        }

        void addNewEvent(Event newEvent) {
            if (mList == null) {
                mList = new ArrayList<>(1);
            }

            int position = 0;
            for (int i = mList.size() - 1; i >= 0; i--) {
                if (mList.get(i).getTime().isBefore(newEvent.getTime())) {
                    position = i + 1;
                    break;
                }
            }

            mList.add(position, newEvent);
            notifyItemInserted(position);

            Log.d(TAG, MessageFormat.format("A new item added to the position {0}.", position));
        }

        void updateAnEventAt(Event updatedEvent, int position) {
            if (mList.get(position).getID() != updatedEvent.getID()) {
                Log.d(TAG, MessageFormat.format("Updated item ID {0} does NOT match with the specified position {1}.",
                        updatedEvent.getID(), position));
                return;
            }

            if (mList.get(position).getTime().equals(updatedEvent.getTime())) {
                mList.set(position, updatedEvent);
                notifyItemChanged(position);

                Log.d(TAG, MessageFormat.format("Updated an item at the position {0}.", position));
            } else {
                mList.remove(position);

                int newPosition = 0;
                for (int i = mList.size() - 1; i >= 0; i--) {
                    if (mList.get(i).getTime().isBefore(updatedEvent.getTime()) ||
                            (mList.get(i).getTime().isEqual(updatedEvent.getTime())
                                    && mList.get(i).getID() < updatedEvent.getID())) {
                        newPosition = i + 1;
                        break;
                    }
                }

                mList.add(newPosition, updatedEvent);

                notifyItemMoved(position, newPosition);
                notifyItemChanged(newPosition);
            }
        }

        void deleteAnEventAt(Event deletedEvent, int position) {
            if (mList.get(position).getID() != deletedEvent.getID()) {
                Log.d(TAG, MessageFormat.format("Deleted item ID {0} does NOT match with the specified position {1}.",
                        deletedEvent.getID(), position));
                return;
            }

            mList.remove(position);
            notifyItemRemoved(position);

            Log.d(TAG, MessageFormat.format("Removed an item at the position {0}.", position));
        }

        void refreshIfTimeFormatChanged(boolean is24HourFormat) {
            if (is24HourFormat != mIs24HourFormat) {
                mIs24HourFormat = is24HourFormat;
                notifyDataSetChanged();
            }
        }

        class ViewHolder extends RecyclerView.ViewHolder
                implements View.OnClickListener {
            final TextView tvTitle, tvDescription, tvTime;
            final ImageView ivIcon;

            private final OnItemClickListener mClickListener;

            ViewHolder(EventModelAdapter adapter, View itemView) {
                super(itemView);

                tvTitle = itemView.findViewById(R.id.tvTitle);
                tvDescription = itemView.findViewById(R.id.tvDescription);
                tvTime = itemView.findViewById(R.id.tvTime);
                ivIcon = itemView.findViewById(R.id.ivIcon);

                itemView.setOnClickListener(this);
                //itemView.setOnLongClickListener(this);

                this.mClickListener = adapter;
            }

            @Override
            public void onClick(View view) {
                Log.d(TAG, "Item clicked on position " + getAdapterPosition());
                if (getAdapterPosition() >= 0) {
                    mClickListener.onClick(view, getAdapterPosition());
                }
            }

        /*@Override
        public boolean onLongClick(View view) {
            Log.d(TAG, "Item long clicked on position " + getAdapterPosition());

            Vibrator vibrator = (Vibrator) view.getContext().getSystemService(Context.VIBRATOR_SERVICE);
            vibrator.vibrate(300);

            return mClickListener.onClick(view, getAdapterPosition(), true);
        }*/
        }
    }
}

